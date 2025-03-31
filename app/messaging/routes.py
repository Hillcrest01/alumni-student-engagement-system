from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Message, User

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/send/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Message cannot be empty', 'danger')
            return redirect(url_for('messaging.send_message', recipient_id=recipient_id))
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=recipient.id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('messaging.view_conversation', recipient_id=recipient_id))
    
    return render_template('messaging/send_message.html', recipient=recipient)

@messaging_bp.route('/conversation/<int:recipient_id>')
@login_required
def view_conversation(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == recipient_id)) |
        ((Message.sender_id == recipient_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    Message.query.filter_by(receiver_id=current_user.id, sender_id=recipient_id).update({'read': True})
    db.session.commit()
    
    return render_template('messaging/conversation.html', 
                         recipient=recipient,
                         messages=messages)

@messaging_bp.route('/inbox')
@login_required
def inbox():
    # Get all conversations with unread count
    conversations = db.session.query(
        User,
        db.func.max(Message.timestamp).label('last_message_time'),
        db.func.sum(
            db.case(  # Remove the list wrapper []
                (
                    db.and_(
                        Message.receiver_id == current_user.id,
                        Message.read == False,
                        User.id == Message.sender_id
                    ), 
                    1
                ),
                else_=0
            )
        ).label('unread_count')
    ).join(
        Message,
        (User.id == Message.sender_id) | (User.id == Message.receiver_id)
    ).filter(
        (Message.sender_id == current_user.id) |
        (Message.receiver_id == current_user.id),
        User.id != current_user.id
    ).group_by(User.id).order_by(db.desc('last_message_time')).all()

    return render_template('messaging/inbox.html', conversations=conversations)