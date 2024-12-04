import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger("FeedbackCollector")

class FeedbackCollector:
    def __init__(self):
        self.feedback_file = "data/user_feedback.csv"
        self.ensure_feedback_file_exists()

    def ensure_feedback_file_exists(self):
        """Create feedback file with headers if it doesn't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists(self.feedback_file):
            headers = [
                "timestamp",
                "user_query",
                "selected_services",
                "accuracy_rating",
                "relevance_rating",
                "missing_services",
                "unnecessary_services",
                "additional_comments",
                "would_use_again"
            ]
            pd.DataFrame(columns=headers).to_csv(self.feedback_file, index=False)
            logger.info(f"Created new feedback file at {self.feedback_file}")

    def save_feedback(self, feedback_data: Dict[str, Any]):
        """Save user feedback to CSV file"""
        try:
            feedback_data["timestamp"] = datetime.now().isoformat()
            
            # Convert lists to string representation
            for key in ["selected_services", "missing_services", "unnecessary_services"]:
                if key in feedback_data and isinstance(feedback_data[key], list):
                    feedback_data[key] = ", ".join(feedback_data[key])

            # Read existing data
            df = pd.read_csv(self.feedback_file)
            
            # Append new feedback
            new_df = pd.DataFrame([feedback_data])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.feedback_file, index=False)
            logger.info("Successfully saved user feedback")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return False

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get basic statistics from collected feedback"""
        try:
            df = pd.read_csv(self.feedback_file)
            stats = {
                "total_responses": len(df),
                "average_accuracy": df["accuracy_rating"].mean(),
                "average_relevance": df["relevance_rating"].mean(),
                "would_use_again_percentage": (df["would_use_again"] == True).mean() * 100,
                "most_common_missing_services": self._get_most_common_items(df, "missing_services"),
                "most_common_unnecessary_services": self._get_most_common_items(df, "unnecessary_services")
            }
            return stats
        except Exception as e:
            logger.error(f"Error calculating feedback stats: {str(e)}")
            return {}

    def _get_most_common_items(self, df: pd.DataFrame, column: str, top_n: int = 5) -> List[str]:
        """Helper function to get most common items from a comma-separated string column"""
        try:
            all_items = []
            for items_str in df[column].dropna():
                all_items.extend([item.strip() for item in items_str.split(",")])
            
            from collections import Counter
            return [item for item, _ in Counter(all_items).most_common(top_n)]
        except Exception:
            return [] 