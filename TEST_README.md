# Furillo Test Suite

This directory contains comprehensive test cases for the Furillo Flask application.

## Test Coverage

The test suite covers the following areas:

### 1. Authentication Tests
- User registration (success/failure cases)
- NGO registration
- Login/logout functionality
- Duplicate username/email handling
- Invalid credentials

### 2. User Profile Tests
- User questionnaire completion
- Pet profile creation
- Profile data validation

### 3. NGO Tests
- NGO profile management
- NGO pet profile creation
- NGO-specific functionality

### 4. Adoption Tests
- Viewing adoption posts
- Creating adoption requests
- Managing adoption requests (NGO)
- Status updates

### 5. Lost Pet Tests
- Reporting lost pets
- Updating lost pet status
- Lost pet management

### 6. Campaign Tests
- Publishing campaigns
- Responding to campaigns
- Deleting campaigns
- Campaign management

### 7. Rescue Alert Tests
- Creating rescue alerts
- Updating rescue status
- Deleting rescue alerts

### 8. Message Tests
- Adoption conversations
- Lost pet conversations
- Rescue conversations
- Message sending/receiving

### 9. File Upload Tests
- Pet image uploads
- Campaign image uploads

### 10. Dashboard Tests
- User dashboard access
- NGO dashboard access
- About page functionality

### 11. Error Handling Tests
- 404 errors
- Unauthorized access
- Invalid user type access

### 12. Data Validation Tests
- Email format validation
- Password strength
- Required field validation

### 13. Performance Tests
- Multiple user registrations
- Multiple campaign creation
- Database query performance

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r test_requirements.txt
```

### Running All Tests
```bash
# Using the test runner
python run_tests.py

# Or using unittest directly
python -m unittest test_app.py -v

# Or using pytest (if installed)
pytest test_app.py -v
```

### Running Specific Test Classes
```bash
# Run only authentication tests
python -m unittest test_app.AuthenticationTests -v

# Run only adoption tests
python -m unittest test_app.AdoptionTests -v

# Run only campaign tests
python -m unittest test_app.CampaignTests -v
```

### Running Specific Test Methods
```bash
# Run a specific test method
python -m unittest test_app.AuthenticationTests.test_register_user_success -v
```

## Test Configuration

### Test Database
- Tests use a temporary SQLite database
- Database is created fresh for each test
- Database is cleaned up after each test

### Test Users
- `testuser` (regular user)
- `testngo` (NGO user)
- Both users are created with complete profiles

### Test Data
- Sample pets for adoption
- Sample campaigns
- Sample adoption requests
- Sample lost pet reports
- Sample rescue alerts

## Test Structure

### Base Test Class
```python
class FurilloTestCase(unittest.TestCase):
    def setUp(self):
        # Create temporary database
        # Create test users
        # Set up test environment
    
    def tearDown(self):
        # Clean up database
        # Remove temporary files
```

### Helper Methods
- `login_user()` - Login as regular user
- `login_ngo()` - Login as NGO user
- `create_test_users()` - Create test users

## Test Categories

### CRUD Operations
- **Create**: Users, pets, campaigns, adoption requests, lost pet reports, rescue alerts, messages
- **Read**: Dashboard views, profile pages, adoption listings
- **Update**: Profile updates, status changes, message sending
- **Delete**: Campaigns, rescue alerts, adoption requests

### Edge Cases
- Duplicate data handling
- Invalid input validation
- Authorization checks
- File upload scenarios
- Error conditions

### Performance
- Multiple concurrent operations
- Database query optimization
- Memory usage patterns

## Troubleshooting

### Common Issues

1. **Template Errors**
   - Fixed: `request` variable conflict in templates
   - Updated: Template variable names to avoid conflicts

2. **Database Warnings**
   - Fixed: SQLAlchemy deprecated `.get()` method
   - Updated: Using `db.session.get()` instead

3. **Test Failures**
   - Some POST requests may not create records due to backend logic
   - Tests are designed to handle both success and failure scenarios

### Debugging Tests
```bash
# Run with maximum verbosity
python -m unittest test_app.py -v

# Run with debug output
python -c "
import unittest
import test_app
unittest.main(verbosity=2)
"
```

## Adding New Tests

### Test Naming Convention
- Test classes: `FeatureTests` (e.g., `AuthenticationTests`)
- Test methods: `test_feature_action` (e.g., `test_register_user_success`)

### Example Test Method
```python
def test_new_feature(self):
    """Test description"""
    # Arrange
    # Act
    response = self.app.post('/endpoint', data={...})
    # Assert
    self.assertEqual(response.status_code, 200)
    # Additional assertions...
```

### Test Data Setup
```python
def setUp(self):
    super().setUp()
    # Create additional test data
    self.test_data = {...}
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    - name: Run tests
      run: python run_tests.py
```

## Coverage Report

To generate a coverage report:
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest test_app.py

# Generate report
coverage report

# Generate HTML report
coverage html
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up after tests
3. **Descriptive Names**: Use clear, descriptive test names
4. **Documentation**: Add docstrings to test methods
5. **Edge Cases**: Test both success and failure scenarios
6. **Performance**: Consider performance implications of tests

## Maintenance

### Regular Tasks
- Update tests when new features are added
- Review and update test data as needed
- Monitor test execution time
- Update dependencies as needed

### Test Data Management
- Keep test data minimal but realistic
- Use factories for complex test data
- Clean up test data after each test
- Avoid hardcoded values in assertions 