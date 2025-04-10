import io
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.models import User, Event, Job, VerificationRequest

def generate_system_report(start_date=None, end_date=None):
    """Generate a comprehensive system report PDF"""
    # Data collection
    users = User.query.all()
    events = Event.query.all()
    jobs = Job.query.all()
    verifications = VerificationRequest.query.all()
    active_alumni = [u for u in users if u.role == 'alumni' and u.availability == 'available']

    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Get default styles and modify them
    styles = getSampleStyleSheet()
    
    # Modify existing styles
    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].textColor = colors.HexColor('#157347')
    styles['Title'].spaceAfter = 20
    
    styles['Heading2'].fontName = 'Helvetica-Bold'
    styles['Heading2'].textColor = colors.HexColor('#161F37')
    styles['Heading2'].spaceAfter = 10
    
    styles['BodyText'].fontName = 'Helvetica'
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 12

    # Create footer style
    footer_style = ParagraphStyle(
        name='FooterStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add title and metadata
    elements.append(Paragraph("ALUMNI SYSTEM REPORT", styles['Title']))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", 
                            styles['BodyText']))
    if start_date and end_date:
        elements.append(Paragraph(f"Date Range: {start_date} to {end_date}", styles['BodyText']))
    elements.append(Spacer(1, 20))
    
    # System Summary Table
    elements.append(Paragraph("System Summary", styles['Heading2']))
    summary_data = [
        ['Metric', 'Count'],
        ['Total Users', len(users)],
        ['Administrators', sum(1 for u in users if u.is_admin())],
        ['Verified Users', sum(1 for u in users if u.is_verified)],
        ['Active Alumni', len(active_alumni)],
        ['Total Events', len(events)],
        ['Upcoming Events', sum(1 for e in events if e.date_time > datetime.now())],
        ['Total Job Postings', len(jobs)],
        ['Verified Job Postings', sum(1 for j in jobs if j.is_verified)],
        ['Verification Requests', len(verifications)]
    ]
    summary_table = Table(summary_data, colWidths=[200, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#157347')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#161F37'))
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # User Statistics Section
    elements.append(Paragraph("User Statistics", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Add user roles chart
    user_roles_chart = generate_user_roles_chart(users)
    elements.append(Image(user_roles_chart, width=500, height=300))
    elements.append(Spacer(1, 15))
    
    # User details table
    recent_users = sorted(users, key=lambda x: x.created_at, reverse=True)[:5]
    user_data = [['Name', 'Email', 'Role', 'Verified', 'Joined']] + [
        [u.full_name or u.email.split('@')[0], u.email, u.role.capitalize(), 
         'Yes' if u.is_verified else 'No', u.created_at.strftime('%Y-%m-%d')] 
        for u in recent_users
    ]
    user_table = Table(user_data, colWidths=[120, 150, 80, 60, 80])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E6C200')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#161F37')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    elements.append(user_table)
    elements.append(PageBreak())
    
    # Event Statistics Section
    elements.append(Paragraph("Event Statistics", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Add events chart
    events_chart = generate_events_chart(events)
    elements.append(Image(events_chart, width=500, height=300))
    elements.append(Spacer(1, 15))
    
    # Recent events table
    recent_events = sorted(events, key=lambda x: x.date_time, reverse=True)[:5]
    event_data = [['Title', 'Date', 'Location']] + [
        [e.title, e.date_time.strftime('%Y-%m-%d'), e.location] 
        for e in recent_events
    ]
    event_table = Table(event_data, colWidths=[180, 80, 120, 80])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#157347')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    elements.append(event_table)
    elements.append(PageBreak())
    
    # Verification Statistics Section
    elements.append(Paragraph("Verification Statistics", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # Add verification chart
    verification_chart = generate_verification_chart(verifications)
    elements.append(Image(verification_chart, width=500, height=300))
    elements.append(Spacer(1, 15))
    
    # Recent verifications table
    recent_verifications = sorted(verifications, key=lambda x: x.created_at, reverse=True)[:5]
    verification_data = [['Email', 'Status', 'Requested', 'Reviewed']] + [
        [v.email, v.status.capitalize(), 
         v.created_at.strftime('%Y-%m-%d'),
         v.reviewed_at.strftime('%Y-%m-%d') if v.reviewed_at else 'Pending']
        for v in recent_verifications
    ]
    verification_table = Table(verification_data, colWidths=[150, 80, 80, 80])
    verification_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E6C200')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#161F37')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    elements.append(verification_table)
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Confidential - For internal use only", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_user_roles_chart(users):
    """Generate user roles pie chart"""
    fig, ax = plt.subplots(figsize=(8, 5))
    roles = pd.Series([user.role for user in users]).value_counts()
    
    # Use brand colors
    colors = ['#157347', '#E6C200', '#161F37']
    ax.pie(roles, labels=roles.index, autopct='%1.1f%%', 
           colors=colors, startangle=90, textprops={'fontsize': 10})
    ax.set_title('User Roles Distribution', pad=20, fontweight='bold')
    
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    plt.close(fig)
    return buf

def generate_events_chart(events):
    """Generate monthly events bar chart"""
    fig, ax = plt.subplots(figsize=(8, 5))
    event_dates = [event.date_time for event in events]
    
    # Group by month
    monthly_events = pd.Series(event_dates).dt.to_period('M').value_counts().sort_index()
    monthly_events.index = monthly_events.index.strftime('%b %Y')
    
    ax.bar(monthly_events.index, monthly_events, color='#157347')
    ax.set_title('Events Per Month', pad=15, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Events')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    plt.close(fig)
    return buf

def generate_verification_chart(verifications):
    """Generate verification status chart"""
    fig, ax = plt.subplots(figsize=(8, 4))
    status_counts = pd.Series([v.status for v in verifications]).value_counts()
    
    # Corrected colors
    colors = {
        'approved': '#157347',
        'pending': '#E6C200',
        'rejected': '#dc3545'
    }
    status_counts.plot(kind='barh', ax=ax, 
                      color=[colors.get(s, '#999999') for s in status_counts.index])
    
    ax.set_title('Verification Request Status', pad=15, fontweight='bold')
    ax.set_xlabel('Number of Requests')
    plt.tight_layout()
    
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    plt.close(fig)
    return buf