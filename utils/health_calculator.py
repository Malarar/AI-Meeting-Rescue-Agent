"""
Health Calculator Module

Calculates meeting health scores based on various analysis metrics.
"""


class HealthCalculator:
    """
    Calculates meeting health score based on analysis metrics.
    
    Scoring system:
    - Base score: 100
    - Confusion score: penalize up to -40 points
    - Decisions count: reward up to +20 points
    - Action items: penalize -20 if zero, -10 if more than 10
    - Blockers: penalize up to -30 points
    - Unassigned tasks: penalize up to -10 points
    
    Status levels:
    - healthy (≥75): ✅
    - at-risk (50-74): ⚠️
    - critical (<50): 🔴
    """
    
    @staticmethod
    def calculate(
        confusion_score: float,
        decisions_count: int,
        action_items_count: int,
        blockers_count: int,
        unassigned_tasks: int
    ) -> dict:
        """
        Calculate meeting health score and status.
        
        Args:
            confusion_score: Confusion score (0-1 range expected)
            decisions_count: Number of decisions made
            action_items_count: Number of action items
            blockers_count: Number of blockers identified
            unassigned_tasks: Number of unassigned tasks
            
        Returns:
            dict: Contains score, status, emoji, and recommendations
        """
        # Start with base score of 100
        score = 100.0
        
        # Penalize for confusion (up to -40 points)
        confusion_penalty = confusion_score * 40
        score -= confusion_penalty
        
        # Reward for decisions (up to +20 points)
        decisions_reward = min(decisions_count * 4, 20)
        score += decisions_reward
        
        # Penalize for action items
        if action_items_count == 0:
            score -= 20
        elif action_items_count > 10:
            score -= 10
        
        # Penalize for blockers (up to -30 points)
        blockers_penalty = min(blockers_count * 10, 30)
        score -= blockers_penalty
        
        # Penalize for unassigned tasks (up to -10 points)
        unassigned_penalty = min(unassigned_tasks * 5, 10)
        score -= unassigned_penalty
        
        # Ensure score stays within 0-100 range
        score = max(0.0, min(100.0, score))
        
        # Determine status and emoji
        if score >= 75:
            status = "healthy"
            emoji = "✅"
        elif score >= 50:
            status = "at-risk"
            emoji = "⚠️"
        else:
            status = "critical"
            emoji = "🔴"
        
        # Generate recommendations
        recommendations = HealthCalculator._generate_recommendations(
            confusion_score=confusion_score,
            decisions_count=decisions_count,
            action_items_count=action_items_count,
            blockers_count=blockers_count,
            unassigned_tasks=unassigned_tasks,
            score=score
        )
        
        return {
            "score": round(score, 2),
            "status": status,
            "emoji": emoji,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _generate_recommendations(
        confusion_score: float,
        decisions_count: int,
        action_items_count: int,
        blockers_count: int,
        unassigned_tasks: int,
        score: float
    ) -> list:
        """
        Generate actionable recommendations based on metrics.
        
        Args:
            confusion_score: Confusion score (0-1 range)
            decisions_count: Number of decisions made
            action_items_count: Number of action items
            blockers_count: Number of blockers identified
            unassigned_tasks: Number of unassigned tasks
            score: Calculated health score
            
        Returns:
            list: List of recommendation strings
        """
        recommendations = []
        
        # High confusion
        if confusion_score > 0.5:
            recommendations.append(
                "High confusion detected. Schedule a follow-up meeting to clarify unclear topics."
            )
        elif confusion_score > 0.3:
            recommendations.append(
                "Moderate confusion present. Send a summary email to align understanding."
            )
        
        # Low decisions
        if decisions_count == 0:
            recommendations.append(
                "No decisions were made. Ensure the next meeting has clear decision points."
            )
        elif decisions_count < 2:
            recommendations.append(
                "Few decisions made. Consider if the meeting achieved its objectives."
            )
        
        # Action items issues
        if action_items_count == 0:
            recommendations.append(
                "No action items identified. Define clear next steps to maintain momentum."
            )
        elif action_items_count > 10:
            recommendations.append(
                "Too many action items. Prioritize the most critical tasks to avoid overwhelm."
            )
        
        # Blockers present
        if blockers_count > 0:
            if blockers_count >= 3:
                recommendations.append(
                    f"{blockers_count} blockers identified. Urgently address these to prevent project delays."
                )
            else:
                recommendations.append(
                    f"{blockers_count} blocker(s) identified. Assign owners and set resolution deadlines."
                )
        
        # Unassigned tasks
        if unassigned_tasks > 0:
            recommendations.append(
                f"{unassigned_tasks} task(s) unassigned. Assign owners to ensure accountability."
            )
        
        # Overall health recommendations
        if score < 50:
            recommendations.append(
                "Meeting health is critical. Consider restructuring future meetings for better outcomes."
            )
        elif score < 75:
            recommendations.append(
                "Meeting health is at-risk. Review meeting structure and participant engagement."
            )
        
        # If no specific issues, provide positive feedback
        if not recommendations:
            recommendations.append(
                "Meeting health is excellent. Continue with current meeting practices."
            )
        
        return recommendations

# Made with Bob
