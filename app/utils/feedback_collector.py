import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

class FeedbackCollector:
    def __init__(self, feedback_dir="data"):
        """Initialize feedback collector with configurable directory"""
        self.feedback_dir = feedback_dir
        self.feedback_file = os.path.join(feedback_dir, "user_feedback.csv")
        self.logger = logging.getLogger("FeedbackCollector")
        self.ensure_feedback_file_exists()

    def ensure_feedback_file_exists(self):
        """Create feedback file with headers if it doesn't exist"""
        if not os.path.exists(self.feedback_dir):
            os.makedirs(self.feedback_dir)
            
        if not os.path.exists(self.feedback_file):
            headers = [
                "timestamp",
                "user_name",
                "conversation_history",
                "query_summary",
                "app_rating",
                "selected_services",
                "accuracy_rating",
                "relevance_rating",
                "missing_services",
                "unnecessary_services",
                "overall_experience",
                "other_suggestions",
                "would_use_again"
            ]
            pd.DataFrame(columns=headers).to_csv(self.feedback_file, index=False)
            self.logger.info(f"Created new feedback file at {self.feedback_file}")

    def save_feedback(self, feedback_data: Dict[str, Any]):
        """Save user feedback to CSV file"""
        try:
            feedback_data["timestamp"] = datetime.now().isoformat()
            
            # Convert lists and conversation history to string representation
            for key in ["selected_services", "missing_services", "unnecessary_services"]:
                if key in feedback_data and isinstance(feedback_data[key], list):
                    feedback_data[key] = ", ".join(str(item) for item in feedback_data[key])

            # Format conversation history
            if "conversation_history" in feedback_data and isinstance(feedback_data["conversation_history"], list):
                formatted_history = []
                for msg in feedback_data["conversation_history"]:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    formatted_history.append(f"{role}: {content}")
                feedback_data["conversation_history"] = "\n".join(formatted_history)

            # Read existing data
            df = pd.read_csv(self.feedback_file)
            
            # Append new feedback
            new_df = pd.DataFrame([feedback_data])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.feedback_file, index=False)
            self.logger.info("Successfully saved user feedback with conversation history")
            return True
        except Exception as e:
            self.logger.error(f"Error saving feedback: {str(e)}")
            return False

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get basic statistics from collected feedback"""
        try:
            df = pd.read_csv(self.feedback_file)
            stats = {
                "total_responses": len(df),
                "average_app_rating": df["app_rating"].mean(),
                "average_accuracy": df["accuracy_rating"].mean(),
                "average_relevance": df["relevance_rating"].mean(),
                "would_use_again_percentage": (df["would_use_again"] == True).mean() * 100,
                "most_common_missing_services": self._get_most_common_items(df, "missing_services"),
                "most_common_unnecessary_services": self._get_most_common_items(df, "unnecessary_services")
            }
            return stats
        except Exception as e:
            self.logger.error(f"Error calculating feedback stats: {str(e)}")
            return {}

    def _get_most_common_items(self, df: pd.DataFrame, column: str, top_n: int = 5) -> List[str]:
        """Helper function to get most common items from a comma-separated string column"""
        try:
            all_items = []
            for items_str in df[column].dropna():
                all_items.extend([item.strip() for item in str(items_str).split(",")])
            
            from collections import Counter
            return [item for item, _ in Counter(all_items).most_common(top_n)]
        except Exception:
            return [] 