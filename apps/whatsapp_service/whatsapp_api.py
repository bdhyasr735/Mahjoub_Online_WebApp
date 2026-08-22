try:
    response = requests.post(url, headers=headers, json=payload)
    res_data = response.json()
    
    db = get_db()
    from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
    
    wamid = None
    try:
        wamid = res_data.get('messages', [{}])[0].get('id')
    except:
        pass
        
    status = 'sent' if response.status_code == 200 else 'failed'
    
    # حفظ السجل
    log_entry = WhatsAppMessageLog(
        wamid=wamid,
        direction='outbound', 
        sender_number=PHONE_NUMBER_ID, 
        recipient_number=recipient, 
        content=message, 
        status=status
    )
    db.session.add(log_entry)

    # تحديث آخر رسالة وجهة الاتصال
    contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
    if contact:
        contact.last_message = message
        contact.last_timestamp = datetime.utcnow()
        
    db.session.commit()

    if response.status_code == 200:
        return True, res_data
    else:
        return False, response.text
except Exception as e:
    return False, str(e)
