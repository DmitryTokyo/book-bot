import pytest


def test_check_template(client):
    template_data = b'Well done!'

    response = client.get('/')

    assert response.status_code == 200
    assert template_data in response.data


@pytest.mark.parametrize(
    'template_data, webhook_result',
    [
        (b'webhook setup ok!!!', 'webhook'),
        (b'webhook setup failed', None),
    ],
)
def test_webhook_set_template(mocker, client, template_data, webhook_result):
    mock_result = mocker.patch('bot.app.bot')
    mock_result.setWebhook.return_value = webhook_result
    mocker.patch('bot.app.os')

    response = client.get('/webhook')

    assert response.status_code == 200
    assert template_data in response.data
