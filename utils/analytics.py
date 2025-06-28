import streamlit as st
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

class AnalyticsManager:
    """Analytics and data management for resume analysis history"""

    def __init__(self):
        self.db_path = "resume_analytics.db"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    file_name TEXT,
                    file_type TEXT,
                    overall_score INTEGER,
                    content_quality INTEGER,
                    skills_relevance INTEGER,
                    experience_depth INTEGER,
                    formatting INTEGER,
                    ats_compatibility INTEGER,
                    quantified_impact INTEGER,
                    word_count INTEGER,
                    analysis_data TEXT,
                    session_id TEXT
                )
            """)

            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    rating INTEGER,
                    feedback_text TEXT,
                    feature_used TEXT,
                    session_id TEXT
                )
            """)

            # Create usage statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    feature_name TEXT,
                    action TEXT,
                    session_id TEXT
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            st.error(f"Database initialization error: {e}")

    def save_analysis(self, analysis_data: Dict[str, Any], file_info: Dict[str, str]) -> bool:
        """Save analysis results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Extract scores
            scores = analysis_data.get("category_scores", {})

            cursor.execute("""
                INSERT INTO analysis_history 
                (timestamp, file_name, file_type, overall_score, content_quality, 
                 skills_relevance, experience_depth, formatting, ats_compatibility, 
                 quantified_impact, word_count, analysis_data, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                file_info.get("file_name", "Unknown"),
                file_info.get("file_type", "Unknown"),
                analysis_data.get("overall_score", 0),
                scores.get("content_quality", {}).get("score", 0),
                scores.get("skills_relevance", {}).get("score", 0),
                scores.get("experience_depth", {}).get("score", 0),
                scores.get("formatting", {}).get("score", 0),
                scores.get("ats_compatibility", {}).get("score", 0),
                scores.get("quantified_impact", {}).get("score", 0),
                file_info.get("word_count", 0),
                json.dumps(analysis_data),
                st.session_state.get("session_id", "unknown")
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            st.error(f"Error saving analysis: {e}")
            return False

    def save_feedback(self, rating: int, feedback_text: str, feature_used: str) -> bool:
        """Save user feedback to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO user_feedback 
                (timestamp, rating, feedback_text, feature_used, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                rating,
                feedback_text,
                feature_used,
                st.session_state.get("session_id", "unknown")
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            st.error(f"Error saving feedback: {e}")
            return False

    def log_usage(self, feature_name: str, action: str):
        """Log feature usage for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usage_stats 
                (timestamp, feature_name, action, session_id)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                feature_name,
                action,
                st.session_state.get("session_id", "unknown")
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            # Silently fail for usage logging
            pass

    def get_analysis_history(self, limit: int = 50) -> pd.DataFrame:
        """Get analysis history as DataFrame"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT timestamp, file_name, file_type, overall_score, 
                       content_quality, skills_relevance, experience_depth, 
                       formatting, ats_compatibility, quantified_impact, word_count
                FROM analysis_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """

            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()

            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df

        except Exception as e:
            st.error(f"Error retrieving analysis history: {e}")
            return pd.DataFrame()

    def get_score_trends(self, days: int = 30) -> pd.DataFrame:
        """Get score trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            query = """
                SELECT DATE(timestamp) as date, 
                       AVG(overall_score) as avg_score,
                       COUNT(*) as analysis_count
                FROM analysis_history 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """

            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            st.error(f"Error retrieving score trends: {e}")
            return pd.DataFrame()

    def get_category_performance(self) -> pd.DataFrame:
        """Get average performance by category"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT 
                    AVG(content_quality) as content_quality,
                    AVG(skills_relevance) as skills_relevance,
                    AVG(experience_depth) as experience_depth,
                    AVG(formatting) as formatting,
                    AVG(ats_compatibility) as ats_compatibility,
                    AVG(quantified_impact) as quantified_impact
                FROM analysis_history
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            if not df.empty:
                # Transform to long format for plotting
                categories = []
                scores = []

                for col in df.columns:
                    categories.append(col.replace('_', ' ').title())
                    scores.append(df[col].iloc[0] if not pd.isna(df[col].iloc[0]) else 0)

                return pd.DataFrame({
                    'Category': categories,
                    'Average Score': scores
                })

            return pd.DataFrame()

        except Exception as e:
            st.error(f"Error retrieving category performance: {e}")
            return pd.DataFrame()

    def get_file_type_stats(self) -> pd.DataFrame:
        """Get statistics by file type"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT file_type, 
                       COUNT(*) as count,
                       AVG(overall_score) as avg_score
                FROM analysis_history 
                GROUP BY file_type
                ORDER BY count DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            return df

        except Exception as e:
            st.error(f"Error retrieving file type stats: {e}")
            return pd.DataFrame()

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Total analyses
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM analysis_history")
            total_analyses = cursor.fetchone()[0]

            # Average score
            cursor.execute("SELECT AVG(overall_score) FROM analysis_history")
            avg_score = cursor.fetchone()[0] or 0

            # Most popular features
            cursor.execute("""
                SELECT feature_name, COUNT(*) as usage_count 
                FROM usage_stats 
                GROUP BY feature_name 
                ORDER BY usage_count DESC 
                LIMIT 5
            """)
            popular_features = cursor.fetchall()

            # Recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM analysis_history 
                WHERE timestamp >= ?
            """, (week_ago,))
            recent_analyses = cursor.fetchone()[0]

            conn.close()

            return {
                "total_analyses": total_analyses,
                "average_score": round(avg_score, 1),
                "popular_features": popular_features,
                "recent_analyses": recent_analyses
            }

        except Exception as e:
            st.error(f"Error retrieving usage statistics: {e}")
            return {
                "total_analyses": 0,
                "average_score": 0,
                "popular_features": [],
                "recent_analyses": 0
            }

    def create_score_trend_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create score trend chart"""
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['avg_score'],
            mode='lines+markers',
            line=dict(color='#FF9A8B', width=3),
            marker=dict(size=8, color='#FF9A8B'),
            name='Average Score'
        ))

        fig.update_layout(
            title="Resume Score Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Average Score",
            yaxis=dict(range=[0, 100]),
            template="plotly_white",
            height=400
        )

        return fig

    def create_category_radar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create radar chart for category performance"""
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=df['Average Score'],
            theta=df['Category'],
            fill='toself',
            fillcolor='rgba(255, 154, 139, 0.3)',
            line=dict(color='#FF9A8B', width=2),
            marker=dict(size=8, color='#FF9A8B'),
            name='Performance'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Performance by Category",
            template="plotly_white",
            height=500
        )

        return fig

    def create_file_type_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create file type distribution chart"""
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        colors = ['#FF9A8B', '#A8E6CF', '#88D4F7', '#FFEAA7']

        fig = go.Figure(data=[go.Pie(
            labels=df['file_type'],
            values=df['count'],
            marker_colors=colors[:len(df)],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title="Resume File Types Distribution",
            template="plotly_white",
            height=400
        )

        return fig

    def export_analytics_data(self) -> str:
        """Export analytics data as JSON"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Get all data
            analysis_df = pd.read_sql_query("SELECT * FROM analysis_history", conn)
            feedback_df = pd.read_sql_query("SELECT * FROM user_feedback", conn)
            usage_df = pd.read_sql_query("SELECT * FROM usage_stats", conn)

            conn.close()

            export_data = {
                "export_date": datetime.now().isoformat(),
                "analysis_history": analysis_df.to_dict('records'),
                "user_feedback": feedback_df.to_dict('records'),
                "usage_statistics": usage_df.to_dict('records')
            }

            return json.dumps(export_data, indent=2)

        except Exception as e:
            st.error(f"Error exporting data: {e}")
            return "{}"

# Global analytics manager instance
analytics_manager = AnalyticsManager()
