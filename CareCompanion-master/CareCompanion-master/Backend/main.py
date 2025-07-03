import os
import google.generativeai as genai
# Set Gemini API key from environment variable or hardcode (not recommended for production)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDxub6J1e3AOX6tNW6FGHo334MISfAcLUs")
genai.configure(api_key=GEMINI_API_KEY)

# Function to get advice from Gemini based on alert data
def get_gemini_advice(alert_data):
    prompt = f"""
    You are a healthcare assistant AI. Given the following patient alert data, provide a short, clear, and actionable advice for caregivers. Be specific and concise.
    Patient ID: {alert_data.get('patient_id')}
    Alert Type: {alert_data.get('type')}
    Heart Rate: {alert_data.get('heart_rate')}
    Blood Pressure: {alert_data.get('blood_pressure')}
    Mood Score: {alert_data.get('mood_score')}
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, 'text') else str(response)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "AI advice unavailable (Gemini error)"
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict

# 🔥 1. Initialize Firebase
cred = credentials.Certificate("elderlyappKey.json")  # Ensure this file is in your project root
firebase_admin.initialize_app(cred)
db = firestore.client()



# 🚀 2. Create FastAPI App
app = FastAPI()
# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📜 3. Define Alert Types
class AlertType(str, Enum):
    medication = "medication"
    assistance = "assistance"
    pain = "pain"
    emergency = "emergency"

# 📦 4. Alert Model
class AlertCreate(BaseModel):
    patient_id: str
    type: AlertType
    heart_rate: int
    blood_pressure: str
    mood_score: int

# 🧠 5. EmoSphere AI Logic
class EmoSphere:
    # Define urgency scores for each alert type (higher = more urgent)
    URGENCY_SCORES = {
        AlertType.emergency: 10,
        AlertType.pain: 8,
        AlertType.assistance: 5,
        AlertType.medication: 3
    }

    @staticmethod
    async def analyze_emotion(alert: AlertCreate, patient_id: str) -> Dict:
        """
        Analyze alert to infer emotional urgency and context, using vitals.
        Returns a dictionary with emotional insights.
        """
        # Fetch recent alerts for the patient (last 1 hour) to detect patterns
        recent_alerts = db.collection('alerts')\
            .where('patient_id', '==', patient_id)\
            .where('timestamp', '>=', datetime.now() - timedelta(hours=1))\
            .stream()

        alert_count = sum(1 for _ in recent_alerts)
        base_urgency = EmoSphere.URGENCY_SCORES.get(alert.type, 1)

        # Vitals-based urgency adjustments (reasonable defaults)
        vitals_urgency = 0
        if hasattr(alert, 'heart_rate') and alert.heart_rate:
            if alert.heart_rate > 120 or alert.heart_rate < 50:
                vitals_urgency += 3
            elif alert.heart_rate > 100 or alert.heart_rate < 60:
                vitals_urgency += 1
        if hasattr(alert, 'mood_score') and alert.mood_score:
            if alert.mood_score < 3:
                vitals_urgency += 3
            elif alert.mood_score < 6:
                vitals_urgency += 1
        # Blood pressure: simple string check (expand as needed)
        if hasattr(alert, 'blood_pressure') and alert.blood_pressure:
            try:
                systolic, diastolic = map(int, alert.blood_pressure.split("/"))
                if systolic > 180 or diastolic > 120:
                    vitals_urgency += 3
                elif systolic > 140 or diastolic > 90:
                    vitals_urgency += 1
            except Exception:
                pass  # Ignore if not in expected format

        # Calculate emotional urgency score
        emotional_urgency = base_urgency + vitals_urgency + (alert_count * 2 if alert_count > 1 else 0)

        # Determine emotional context based on score
        if emotional_urgency >= 15:
            emotional_context = "Critical: Immediate attention required"
        elif emotional_urgency >= 10:
            emotional_context = "High: Urgent response needed"
        elif emotional_urgency >= 5:
            emotional_context = "Moderate: Check promptly"
        else:
            emotional_context = "Low: Routine follow-up"

        return {
            'patient_id': patient_id,
            'alert_type': alert.type.value,
            'emotional_urgency': emotional_urgency,
            'emotional_context': emotional_context,
            'heart_rate': getattr(alert, 'heart_rate', None),
            'blood_pressure': getattr(alert, 'blood_pressure', None),
            'mood_score': getattr(alert, 'mood_score', None),
            'timestamp': datetime.now()
        }

    @staticmethod
    async def save_insight(insight: Dict):
        """
        Save emotional insight to Firestore.
        """
        insight_ref = db.collection('emotion_insights').document()
        insight_ref.set(insight)
        return insight_ref.id

# 📡 6. API Endpoint: Create Alert with EmoSphere
@app.post("/alerts/")
async def create_alert(alert: AlertCreate):
    try:
        # Prepare alert data
        alert_data = {
            'patient_id': alert.patient_id,
            'type': alert.type.value,
            'heart_rate': alert.heart_rate,
            'blood_pressure': alert.blood_pressure,
            'mood_score': alert.mood_score,
            'timestamp': datetime.now(),
            'resolved': False
        }

        # Get Gemini AI advice
        ai_advice = get_gemini_advice(alert_data)
        alert_data['ai_advice'] = ai_advice
        if ai_advice == "AI advice unavailable (Gemini error)":
            print("Warning: Gemini AI did not return advice. Check your API key, quota, or network.")

        # Save the alert to Firestore (with AI advice)
        alert_ref = db.collection('alerts').document()
        alert_ref.set(alert_data)

        # Optionally, run EmoSphere analysis and save insight (can be removed if only Gemini is needed)
        # emo_insight = await EmoSphere.analyze_emotion(alert, alert.patient_id)
        # insight_id = await EmoSphere.save_insight(emo_insight)

        # Print or notify with AI advice
        print(f"🚨 New Alert: {alert.type.value} from Patient {alert.patient_id}\nGemini AI Advice: {ai_advice}")

        return {
            "success": True,
            "alert_id": alert_ref.id,
            "ai_advice": ai_advice
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing alert: {str(e)}")

# 🏁 7. Run the Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Axios POST request example (to be used in frontend or API client, not in this file)
# axios.post('http://localhost:8000/alerts/', form)
# axios.get('http://localhost:8000/alerts/')