from submission import helpers


def test_send_email_with_html(mailoutbox):
    helpers.send_email(
        subject='this thing',
        from_email='from@example.com',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        body_text='Hello',
        body_html='<a>Hello</a>',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == 'from@example.com'
    assert message.reply_to == ['reply@example.com']
    assert message.to == ['to@example.com']
    assert message.body == 'Hello'


def test_send_email_without_html(mailoutbox):
    helpers.send_email(
        subject='this thing',
        from_email='from@example.com',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        body_text='Hello',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == 'from@example.com'
    assert message.reply_to == ['reply@example.com']
    assert list(message.to) == ['to@example.com']
    assert message.body == 'Hello'
