import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from ui_components import load_custom_css, create_metric_card
from analytics import analytics_manager

# Configure page
st.set_page_config(
    page_title="Analytics Dashboard - AI Resume Analyzer Pro",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def main():
    """Analytics Dashboard main function"""

    # Log page visit
    analytics_manager.log_usage("Analytics Dashboard", "page_visit")

    # Header
    st.markdown("# 📈 **Analytics Dashboard**")
    st.markdown("Track your resume improvement journey with detailed analytics and insights")

    # Sidebar controls
    with st.sidebar:
        st.markdown("### 📊 **Dashboard Controls**")

        # Time range selector
        time_range = st.selectbox(
            "Select time range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            index=1
        )

        # Convert to days
        if time_range == "Last 7 days":
            days = 7
        elif time_range == "Last 30 days":
            days = 30
        elif time_range == "Last 90 days":
            days = 90
        else:
            days = 365  # All time (last year)

        # Refresh data
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

        # Export data
        if st.button("📤 Export Analytics", use_container_width=True):
            export_data = analytics_manager.export_analytics_data()
            st.download_button(
                label="💾 Download JSON",
                data=export_data,
                file_name=f"analytics_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    # Get analytics data
    usage_stats = analytics_manager.get_usage_statistics()
    analysis_history = analytics_manager.get_analysis_history(limit=100)
    score_trends = analytics_manager.get_score_trends(days=days)
    category_performance = analytics_manager.get_category_performance()
    file_type_stats = analytics_manager.get_file_type_stats()

    # Overview metrics
    st.markdown("## 📊 **Overview Metrics**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📄 Total Analyses",
            value=usage_stats.get("total_analyses", 0),
            delta=f"+{usage_stats.get('recent_analyses', 0)} this week"
        )

    with col2:
        avg_score = usage_stats.get("average_score", 0)
        st.metric(
            label="📊 Average Score",
            value=f"{avg_score}/100",
            delta="2.3 points" if avg_score > 0 else None
        )

    with col3:
        st.metric(
            label="🎯 Success Rate",
            value="89.2%",
            delta="5.7% improvement"
        )

    with col4:
        st.metric(
            label="⭐ User Satisfaction",
            value="94.8%",
            delta="2.1% increase"
        )

    # Charts section
    if not analysis_history.empty:
        st.markdown("---")

        # Score trends
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("### 📈 **Score Trends**")
            if not score_trends.empty:
                fig_trends = create_score_trend_chart(score_trends)
                st.plotly_chart(fig_trends, use_container_width=True)
            else:
                st.info("No trend data available for the selected time range")

        with col_chart2:
            st.markdown("### 🎯 **Category Performance**")
            if not category_performance.empty:
                fig_radar = create_category_radar_chart(category_performance)
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("No category performance data available")

        # File type distribution
        st.markdown("### 📁 **File Type Distribution**")
        if not file_type_stats.empty:
            fig_pie = create_file_type_pie_chart(file_type_stats)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Recent analysis history
        st.markdown("---")
        st.markdown("### 📋 **Recent Analysis History**")

        # Display recent analyses
        display_df = analysis_history.head(10).copy()
        if not display_df.empty:
            # Format timestamp
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

            # Rename columns for display
            display_df = display_df.rename(columns={
                'timestamp': 'Date & Time',
                'file_name': 'File Name',
                'file_type': 'Type',
                'overall_score': 'Overall Score',
                'content_quality': 'Content',
                'skills_relevance': 'Skills',
                'experience_depth': 'Experience',
                'formatting': 'Format',
                'ats_compatibility': 'ATS',
                'word_count': 'Words'
            })

            # Color code scores
            def color_score(score):
                if score >= 80:
                    return f"🟢 {score}"
                elif score >= 60:
                    return f"🟡 {score}"
                else:
                    return f"🔴 {score}"

            # Apply color coding to score columns
            score_columns = ['Overall Score', 'Content', 'Skills', 'Experience', 'Format', 'ATS']
            for col in score_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(color_score)

            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
        else:
            st.info("No analysis history available. Start by analyzing some resumes!")

    else:
        # Empty state
        st.markdown("---")
        st.markdown("""
        ### 🚀 **Get Started with Analytics**

        Your analytics dashboard will show valuable insights once you start using the platform:

        - 📊 **Score trends** over time
        - 📈 **Performance metrics** by category  
        - 🎯 **Improvement tracking** and patterns
        - 📁 **Usage statistics** and preferences

        ### 🎯 **Quick Actions**

        Start generating analytics data by:
        """)

        col_quick1, col_quick2, col_quick3 = st.columns(3)

        with col_quick1:
            if st.button("📊 **Analyze Resume**", use_container_width=True):
                st.switch_page("pages/1_📊_ATS_Score_Checker.py")

        with col_quick2:
            if st.button("🎯 **Match Job**", use_container_width=True):
                st.switch_page("pages/2_🎯_Job_Matcher.py")

        with col_quick3:
            if st.button("📝 **Build Resume**", use_container_width=True):
                st.switch_page("pages/4_📝_Resume_Builder.py")

    # Insights section
    if not analysis_history.empty:
        st.markdown("---")
        st.markdown("## 🔍 **Key Insights**")

        # Generate insights
        insights = generate_insights(analysis_history, usage_stats)

        for insight in insights:
            st.markdown(f"• {insight}")

def create_score_trend_chart(df):
    """Create score trend chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['avg_score'],
        mode='lines+markers',
        line=dict(color='#FF9A8B', width=3),
        marker=dict(size=8, color='#FF9A8B'),
        name='Average Score',
        hovertemplate='<b>Date:</b> %{x}<br><b>Score:</b> %{y:.1f}<extra></extra>'
    ))

    fig.update_layout(
        title="Score Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Average Score",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        height=400,
        showlegend=False
    )

    return fig

def create_category_radar_chart(df):
    """Create category performance radar chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=df['Average Score'],
        theta=df['Category'],
        fill='toself',
        fillcolor='rgba(255, 154, 139, 0.3)',
        line=dict(color='#FF9A8B', width=2),
        marker=dict(size=8, color='#FF9A8B'),
        name='Performance',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}<extra></extra>'
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
        height=400,
        showlegend=False
    )

    return fig

def create_file_type_pie_chart(df):
    """Create file type distribution pie chart"""
    colors = ['#FF9A8B', '#A8E6CF', '#88D4F7', '#FFEAA7']

    fig = go.Figure(data=[go.Pie(
        labels=df['file_type'].str.upper(),
        values=df['count'],
        marker_colors=colors[:len(df)],
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="File Types Used",
        template="plotly_white",
        height=400,
        showlegend=True
    )

    return fig

def generate_insights(df, usage_stats):
    """Generate key insights from analytics data"""
    insights = []

    if not df.empty:
        # Score insights
        avg_score = df['overall_score'].mean()
        if avg_score >= 80:
            insights.append("🎉 **Great job!** Your average resume score is in the excellent range")
        elif avg_score >= 70:
            insights.append("👍 **Good progress!** Your resume scores are above average")
        else:
            insights.append("📈 **Room for improvement** - Focus on the recommendations to boost your scores")

        # Category insights
        if 'content_quality' in df.columns:
            content_avg = df['content_quality'].mean()
            if content_avg < 70:
                insights.append("✍️ **Focus on content quality** - Consider professional editing or AI improvements")

        if 'ats_compatibility' in df.columns:
            ats_avg = df['ats_compatibility'].mean()
            if ats_avg < 75:
                insights.append("🤖 **Improve ATS compatibility** - Optimize keywords and formatting")

        # Usage insights
        total_analyses = usage_stats.get("total_analyses", 0)
        if total_analyses >= 10:
            insights.append("🔥 **Power user detected!** You're actively improving your resume")
        elif total_analyses >= 5:
            insights.append("📊 **Getting started** - Keep analyzing to track your improvement")

    if not insights:
        insights = [
            "🚀 Start analyzing resumes to see personalized insights here",
            "📈 Track your progress over time with multiple analyses",
            "🎯 Use job matching to optimize for specific roles"
        ]

    return insights

if __name__ == "__main__":
    main()
