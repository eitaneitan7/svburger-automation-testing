import string
import itertools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest
import uuid


# generate random emails for sign-up
def update_user_emails(user_list):
    unique_user_list = []
    for user in user_list:
        unique_id = uuid.uuid4()
        username, domain = user[0].split('@')
        unique_email = f"{username}+{unique_id}@{domain}"
        unique_user_list.append([unique_email, user[1]])
    return unique_user_list


new_user_list = [
    ['alien2212@gmail.com', 'eitan123'],
    ['outsiderssome@gmail.com', 'password2321'],
    ['houseandgarden@gmail.com', 'passpass1212']
]

# Update new_user_list with unique emails
new_user_list = update_user_emails(new_user_list)


@pytest.fixture(scope='function')
def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://svburger1.co.il/#/HomePage')
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


# Sanity functions
def sign_in(setup):
    driver = setup
    driver.find_element(By.XPATH, '//button[text()="Sign In"]').click()
    driver.find_element(By.XPATH, '//input[@placeholder="Enter your email"]').send_keys('eitan@gmail.co.il')
    driver.find_element(By.XPATH, '//input[@placeholder="Enter your password"]').send_keys('eitan123')
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()


def click_and_order_meal(setup):
    driver = setup
    driver.find_element(By.XPATH, '//h5[text()="Combo Meal"]').click()
    driver.find_element(By.XPATH, '/html/body/div/div[2]/div[1]/div/div/button[2]').click()
    driver.find_element(By.XPATH,
                        '/html/body/div/div[2]/div[1]/div/div/div[2]/div/div/div/div[2]/div[4]/div[1]/button').click()


def test_sanity(setup):
    driver = setup
    sign_in(setup)
    click_and_order_meal(setup)
    assert driver.find_element(By.XPATH,
                               '/html/body/div/div[2]/div[1]/div/div/div[2]/div/div/div/div[1]/h1').is_displayed()


# # Trying to sign in with all from inputs valid
@pytest.mark.parametrize("user", new_user_list)
def test_filled_sign_up_form(setup, user):
    driver = setup
    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[1]').send_keys('eitan')
    driver.find_element(By.XPATH, '//form/input[2]').send_keys('leiberman')
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(user[0])
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/button').click()
    assert driver.find_element(By.XPATH, '//h5[text()="Combo Meal"]').is_displayed()


# # Register only with required fields
@pytest.mark.parametrize("user", new_user_list)
def test_required_fields_form(setup, user):
    driver = setup
    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(user[0])
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/button').click()
    assert driver.find_element(By.XPATH, '//h5[text()="Combo Meal"]').is_displayed()


input_names = [
    '',  # 0 characters, should fail
    'e',  # 1 character, should fail
    'ei',  # 2 characters, should fail
    'eit',  # 3 characters, should fail
    'eita'  # 4 characters, should fail
    'eitan',  # 5 characters, should fail
    'eitanl',  # 6 characters, should pass
    'eitanll',  # 7 characters, should pass
    'eitanlle',  # 8 characters, should pass
    'eitanllee',  # 9 characters, should pass
    'eitanlleeb',  # 10 characters, should pass
    'eitanlleebi',  # 11 characters, should fail
]


# # Testing limits of First name input 6-10 length
@pytest.mark.parametrize("user,name_input", [(user, name) for user in new_user_list for name in input_names], )
def test_required_field_and_name(setup, user, name_input):
    driver = setup
    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[1]').send_keys(name_input)
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(user[0])
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/button').click()

    if 6 <= len(name_input) <= 10:
        assert WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//h5[text()="Combo Meal"]')))
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "First name must be between 2 and 10 characters"
        alert.accept()
    except TimeoutException:
        assert False, "Alert not found or incorrect alert text"


# # Testing limits of last name input
@pytest.mark.parametrize("user,name_input", [(user, name) for user in new_user_list for name in input_names], )
def test_required_field_and_last_name(setup, user, name_input):
    driver = setup
    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[2]').send_keys(name_input)
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(user[0])
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(user[1])
    driver.find_element(By.XPATH, '//form/button').click()
    if 6 <= len(name_input) <= 10:
        assert WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//h5[text()="Combo Meal"]')))
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "First name must be between 2 and 10 characters"
        alert.accept()
    except TimeoutException:
        assert False, "Alert not found or incorrect alert text"


mixed_passwords = [
    "abc$123",  # Valid: Contains special character, 7 characters long
    "Passw0rd!",  # Valid: Contains special character, 9 characters long
    "@12abcXYZ",  # Valid: Contains special character, 9 characters long
    "!short1",  # Valid: Contains special character, 7 characters long
    "LongPass#1234",  # Valid: Contains special character, 13 characters long
    "abc123",  # Invalid: No special character
    "short",  # Invalid: Too short, no special character
    "@",  # Invalid: Too short, despite having a special character
    "passwordpassword",  # Invalid: Too long, no special character
    "密码#1234",  # Invalid: Contains non-English characters
    "1234567890123456",  # Invalid: Too long, no special character
    "abc$",  # Invalid: Too short, though has a special character
    "!@#$%^&*()",  # Invalid: Only special characters, no letters or digits
]

# Testing password validatiojn
@pytest.mark.parametrize("user,password", [(user, password) for user in new_user_list for password in mixed_passwords])
def test_form_password_validation(setup, user, password):
    driver = setup
    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(user[0])
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(password)
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(password)
    driver.find_element(By.XPATH, '//form/button').click()

    # Handle valid password case
    if 6 <= len(password) <= 14 and any(char in string.punctuation for char in password):
        assert WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//h5[text()="Combo Meal"]')))
    else:
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            assert alert.text == "Password must be between 6 and 14 characters", ("Alert text does not match expected "
                                                                                  "message")
            alert.accept()
        except TimeoutException:
            assert False, "Alert not found or incorrect alert text for invalid password condition"


# # Check password and confirm password match.
@pytest.mark.parametrize("user,password,confirm_password,should_pass", [
    (user, 'pass123$', 'pass123$', True) for user in new_user_list  # Matching passwords case
] + [
                             (user, 'pass123$', 'diff123$', False) for user in new_user_list
                             # Non-matching passwords case
                         ])
def test_password_confirmation(setup, user, password, confirm_password, should_pass):
    driver = setup
    unique_email, _ = user

    driver.find_element(By.XPATH, '//a[@href="#/SignUp"]').click()
    driver.find_element(By.XPATH, '//form/input[1]').send_keys('eitan')
    driver.find_element(By.XPATH, '//form/input[2]').send_keys('leiberman')
    driver.find_element(By.XPATH, '//form/input[3]').send_keys(unique_email)
    driver.find_element(By.XPATH, '//form/input[4]').send_keys(password)
    driver.find_element(By.XPATH, '//form/input[5]').send_keys(confirm_password)
    driver.find_element(By.XPATH, '//form/button').click()

    if should_pass:
        assert WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//h5[text()="Combo Meal"]')))
    else:
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            expected_alert_text = "password and confirm error"
            assert alert.text == expected_alert_text, f"Expected alert text to be '{expected_alert_text}' but got '{alert.text}'"
            alert.accept()
        except TimeoutException:
            assert False, "Expected an alert for non-matching passwords, but none was found."


# Order page testing
def test_ordering_meal_quantity(setup):
    driver = setup
    sign_in(setup)

    # List of meals to test ordering with XPaths for meals and their parent divs
    meals_to_order_and_parent = [
        ["//h5[@class='card-title' and text()='Combo Meal']", '/html/body/div/div[2]/div[1]/div/div/div/div[1]/div'],
        ["//h5[@class='card-title' and text()='Kids Meal']", '/html/body/div/div[2]/div[1]/div/div/div/div[2]/div'],
        ["//h5[@class='card-title' and text()='Burger']", '/html/body/div/div[2]/div[1]/div/div/div/div[3]/div'],
        ["//h5[@class='card-title' and text()='Vegan']", '/html/body/div/div[2]/div[1]/div/div/div/div[4]/div'],
        ["//h5[@class='card-title' and text()='Sides']", '/html/body/div/div[2]/div[1]/div/div/div/div[5]/div']
    ]

    expected_color_selected = 'rgba(173, 216, 230, 1)'
    expected_color_unselected = 'rgba(255, 255, 255, 1)'

    # Select valid amount of meals and check the color change
    for index, (meal_xpath, parent_xpath) in enumerate(meals_to_order_and_parent[:3]):
        meal_element = driver.find_element(By.XPATH, meal_xpath)
        parent_element = driver.find_element(By.XPATH, parent_xpath)
        meal_element.click()

        # Wait for the background color to change to the expected color
        WebDriverWait(driver, 10).until(
            lambda d: parent_element.value_of_css_property("background-color") == expected_color_selected,
            f"Background color did not change to lightblue for meal at index {index}"
        )

    # Check that the 4th and 5th meals do not change color
    for meal_xpath, parent_xpath in meals_to_order_and_parent[3:]:
        meal_element = driver.find_element(By.XPATH, meal_xpath)
        parent_element = driver.find_element(By.XPATH, parent_xpath)
        meal_element.click()
        actual_color = parent_element.value_of_css_property("background-color")
        assert actual_color == expected_color_unselected, f"Meal at {meal_xpath} changed color incorrectly."

    reserve_button = driver.find_element(By.XPATH, "//button[text()=' Reserve ']")
    reserve_button.click()


# test order confirmation
def click_reserve(driver):
    print("Attempting to click 'Reserve'...")
    reserve_button_xpath = "//button[text()=' Reserve ']"
    try:
        reserve_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, reserve_button_xpath))
        )
        assert reserve_button.is_displayed(), "'Reserve' button is not displayed."
        reserve_button.click()
        print("'Reserve' clicked successfully.")
    except TimeoutException as e:
        assert False, f"Timeout waiting for the 'Reserve' button to be clickable. Exception: {e}"



def select_meals(driver, combination):
    print(f"Selecting meals: {combination}")
    for meal in combination:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//h5[@class='card-title' and text()='{meal}']"))
        ).click()


def enter_table_number(driver, table_number):
    table_number_input_xpath = "//label[contains(text(), 'table No.')]//following::input"
    try:
        table_number_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, table_number_input_xpath))
        )
        assert table_number_input.is_displayed(), "Table number input is not displayed."
        table_number_input.clear()
        table_number_input.send_keys(str(table_number))
        assert table_number_input.get_attribute("value") == str(table_number), "Table number was not entered correctly."
    except TimeoutException as e:
        assert False, f"Timeout waiting for the table number input to be visible. Exception: {e}"


def click_send(driver):
    send_button_xpath = "//button[contains(text(), 'Send')]"
    try:
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, send_button_xpath))
        )
        send_button.click()
        assert send_button.is_displayed(), "'Send' button is not displayed after clicking."
    except TimeoutException as e:
        assert False, f"Timeout waiting for the 'Send' button to be clickable. Exception: {e}"
    except Exception as e:
        assert False, f"An error occurred while clicking the 'Send' button. Exception: {e}"


def verify_summary(driver, meal_prices, combination):
    print("Verifying summary...")
    total_price_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/div[1]/div/div/div[2]/div/div/div/div[2]/h2[1]"))
    )
    total_price_text = total_price_element.text
    total_price = float(total_price_text.split(':')[1].strip().replace('$', ''))
    expected_total = sum(meal_prices[meal] for meal in combination) * 1.1  # Including service charge

    assert expected_total == total_price, f"Expected total {expected_total}, but found {total_price} on summary page."
    print("Summary verified successfully.")


meal_prices = {
    "Combo Meal": 59.0,
    "Kids Meal": 39.0,
    "Burger": 45.0,
    "Vegan": 45.0,
    "Sides": 12.0
}

# # Generate all combinations of 3 meals
meal_combinations = list(itertools.combinations(meal_prices.keys(), 3))


@pytest.mark.parametrize("combination", meal_combinations)
def test_sum_order(setup, combination):
    driver = setup
    sign_in(driver)

    print(f"Testing combination: {combination}")
    select_meals(driver, combination)
    click_reserve(driver)
    enter_table_number(driver, 2)
    click_send(driver)
    verify_summary(driver, meal_prices, combination)
    print(f"Combination {combination} verified successfully.")
    driver.get('https://svburger1.co.il/#/HomePage')


# Test qty per meal

def adjust_meal_quantity(driver, meal_name, quantity):
    print(f"Adjusting quantity for {meal_name} to {quantity}...")
    quantity_input = driver.find_element(By.XPATH,
                                         f"//label[contains(text(), '{meal_name}')]//following-sibling::input")
    quantity_input.clear()
    quantity_input.send_keys(str(quantity))
    print(f"Quantity for {meal_name} adjusted successfully.")


def verify_quantity_input(driver, meal_name, expected_quantity):
    print(f"Verifying quantity for {meal_name}...")
    quantity_input_xpath = f"//label[contains(text(), '{meal_name}')]/following-sibling::input"
    quantity_input = driver.find_element(By.XPATH, quantity_input_xpath)
    actual_quantity = quantity_input.get_attribute("value")
    assert actual_quantity == str(
        expected_quantity), f"Expected quantity {expected_quantity}, but found {actual_quantity}."
    print(f"Quantity for {meal_name} verified successfully.")


meal_combinations = [
    ("Vegan", "abc"),
    ("Burger", 0),
    ("Sides", 1),
    ("Vegan", 2),
    ("Burger", 5),
    ("Sides", 10),
]


@pytest.mark.parametrize("meal_name, quantity", meal_combinations)
def test_adjust_meal_quantities(setup, meal_name, quantity):
    driver = setup
    sign_in(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//h5[@class='card-title' and text()='{meal_name}']"))
    ).click()
    click_reserve(driver)
    adjust_meal_quantity(driver, meal_name, quantity)
    click_send(driver)


@pytest.mark.parametrize("meal_name, quantity", meal_combinations)
def test_adjust_meal_quantities(setup, meal_name, quantity):
    driver = setup
    sign_in(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//h5[@class='card-title' and text()='{meal_name}']"))
    ).click()
    click_reserve(driver)
    adjust_meal_quantity(driver, meal_name, quantity)
    click_send(driver)
    if int(quantity) > 2:
        # Check if there is an error message or any indication of a bug
        error_message_element = driver.find_element(By.XPATH, "//div[@class='error-message']")
        assert error_message_element.is_displayed(), f"Bug: Order went through with {quantity} meals."
