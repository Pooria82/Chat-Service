import pytest
from selenium import webdriver


@pytest.fixture(scope="module")
def browser():
    driver = webdriver.Chrome()  # Ensure you have the ChromeDriver installed and in PATH
    yield driver
    driver.quit()


def test_chat_flow(browser):
    browser.get('http://localhost:8000')

    # Simulate user actions for E2E test
    browser.find_element_by_id('login').send_keys('testuser@example.com')
    browser.find_element_by_id('password').send_keys('testpassword')
    browser.find_element_by_id('login_button').click()

    assert "Dashboard" in browser.title

    # Simulate sending a message in chat
    browser.find_element_by_id('message_input').send_keys('Hello, E2E test!')
    browser.find_element_by_id('send_button').click()

    # Verify the message was sent
    messages = browser.find_elements_by_class_name('chat_message')
    assert any('Hello, E2E test!' in message.text for message in messages)
