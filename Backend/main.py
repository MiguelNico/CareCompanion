from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict

# 🔥 1. Initialize Firebase
cred = credentials.Certificate("Backend/elderlyappKey.json")  # Ensure this file is in your project root
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🚀 2. Create FastAPI App
app = FastAPI()

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
        Analyze alert to infer emotional urgency and context.
        Returns a dictionary with emotional insights.
        """
        # Fetch recent alerts for the patient (last 1 hour) to detect patterns
        recent_alerts = db.collection('alerts')\
            .where('patient_id', '==', patient_id)\
            .where('timestamp', '>=', datetime.now() - timedelta(hours=1))\
            .stream()

        alert_count = sum(1 for _ in recent_alerts)
        base_urgency = EmoSphere.URGENCY_SCORES.get(alert.type, 1)

        # Calculate emotional urgency score
        # Increase urgency if multiple alerts in a short time
        emotional_urgency = base_urgency + (alert_count * 2 if alert_count > 1 else 0)

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
        # Save the alert to Firestore
        alert_ref = db.collection('alerts').document()
        alert_data = {
            'patient_id': alert.patient_id,
            'type': alert.type.value,
            'timestamp': datetime.now(),
            'resolved': False
        }
        alert_ref.set(alert_data)

        # Run EmoSphere analysis
        emo_insight = await EmoSphere.analyze_emotion(alert, alert.patient_id)
        insight_id = await EmoSphere.save_insight(emo_insight)

        # 📢 Notify caregivers with emotional context
        notification = (
            f"🚨 New Alert: {alert.type.value} from Patient {alert.patient_id}\n"
            f"EmoSphere Insight: {emo_insight['emotional_context']} (Urgency: {emo_insight['emotional_urgency']})"
        )
        print(notification)  # Replace with actual notification system later

        return {
            "success": True,
            "alert_id": alert_ref.id,
            "insight_id": insight_id,
            "emotional_context": emo_insight['emotional_context']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing alert: {str(e)}")

# 🏁 7. Run the Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)