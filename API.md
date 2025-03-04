# API Documentation

## Database Schema

### LabOrder
- `order_id` (CharField): Unique identifier for the lab order (format: OR{year}{sequential_number}, e.g., OR23123, OR231234, etc.).
- `patient_name` (CharField): Name of the patient.
- `ip_number` (CharField): IP number of the patient.
- `age` (PositiveIntegerField): Age of the patient.
- `ageunit` (CharField): Unit of age measurement (y: Years, m: Months, d: Days).
- `sex` (CharField): Sex of the patient (M: Male, F: Female).
- `department` (CharField): Department of the patient.
- `unit` (CharField): Unit of the patient.
- `created_at` (DateTimeField): Timestamp when the order was created.
- `status` (CharField): Status of the order (choices: "pending", "completed").
- `tests` (ManyToManyField): Related lab tests.
- `clinical_history` (TextField): Patient's clinical history.
- `username` (CharField): Username of the person who created the order.
- `role` (CharField): Role of the person who created the order.

### LabTest
- `name` (CharField): Name of the lab test.
- `privilege` (PositiveIntegerField): Required privilege level (1: Intern, 2: Postgraduate, 3: Staff).
- `vac_col` (CharField): Vaccination collection information.

### Privilege
- `name` (PositiveIntegerField): Privilege level identifier.

### Patient
- `ip_number` (CharField): Unique IP number of the patient.
- `name` (CharField): Name of the patient.
- `age` (PositiveIntegerField): Age of the patient.
- `sex` (CharField): Sex of the patient.
- `department` (CharField): Department of the patient.
- `history` (TextField): Medical history of the patient.

## API Endpoints

### Lab Orders

#### List all lab orders
```
GET /api/orders/
```
Response: List of all lab orders with their complete details.

#### Search lab orders
```
GET /api/orders/search/
```
Query Parameters:
- `patient_name`: Filter by patient name (partial match)
- `ip_number`: Filter by IP number (partial match)
- `department`: Filter by exact department name
- `status`: Filter by order status
- `date_from`: Filter orders from this date
- `date_to`: Filter orders until this date
- `test_name`: Filter by test name (partial match)
- `age_min`: Filter by minimum age
- `age_max`: Filter by maximum age
- `unit`: Filter by exact unit name
- `created_by`: Filter by creator's username
- `order_by`: Sort results (prefix with '-' for descending order)

Response: Filtered and sorted list of lab orders.

#### Get order statistics
```
GET /api/orders/stats/
```
Query Parameters:
- `date_from`: Start date for statistics
- `date_to`: End date for statistics

Response:
```json
{
    "total_orders": "integer",
    "pending_orders": "integer",
    "completed_orders": "integer",
    "departments": [
        {
            "department": "string",
            "count": "integer"
        }
    ],
    "units": [
        {
            "unit": "string",
            "count": "integer"
        }
    ],
    "tests_ordered": [
        {
            "tests__name": "string",
            "count": "integer"
        }
    ]
}
```

#### Create a new lab order
```
POST /api/orders/
```
Request Body:
```json
{
    "patient_name": "string",
    "ip_number": "string",
    "age": "integer",
    "department": "string",
    "unit": "string",
    "clinical_history": "string",
    "tests": ["integer"] // Array of test IDs
}
```
Note: `username` and `role` are automatically set from the authenticated user.

#### Submit an order
```
POST /api/orders/submit-order/
```
Request Body: Same as creating a new order.

#### Update order status
```
PATCH /api/orders/{order_id}/update-status/
```
Request Body:
```json
{
    "status": "string" // Either "pending" or "completed"
}
```

#### Retrieve a specific lab order
```
GET /api/orders/{order_id}/
```

#### Update a specific lab order
```
PUT /api/orders/{order_id}/
PATCH /api/orders/{order_id}/
```

#### Delete a specific lab order
```
DELETE /api/orders/{order_id}/
```

### Lab Tests

#### List all lab tests
```
GET /api/tests/
```
Query Parameters:
- `privilege`: Filter by privilege level(s)

Response: List of lab tests with id, name, privilege, and vac_col fields.

#### Create a new lab test
```
POST /api/tests/
```
Request Body:
```json
{
    "name": "string",
    "privilege": "integer",
    "vac_col": "string"
}
```

#### Retrieve a specific lab test
```
GET /api/tests/{id}/
```

#### Update a specific lab test
```
PUT /api/tests/{id}/
PATCH /api/tests/{id}/
```

#### Delete a specific lab test
```
DELETE /api/tests/{id}/
```

### Patients

#### List all patients
```
GET /api/patients/
```
Response:
```json
[
  {
    "ip_number": "string",
    "name": "string",
    "age": "integer",
    "sex": "string",
    "department": "string",
    "history": "string"
  }
]
```

#### Create a new patient
```
POST /api/patients/
```
Request Body:
```json
{
  "ip_number": "string",
  "name": "string",
  "age": "integer",
  "sex": "string",
  "department": "string",
  "history": "string"
}
```
Response:
```json
{
  "ip_number": "string",
  "name": "string",
  "age": "integer",
  "sex": "string",
  "department": "string",
  "history": "string"
}
```

#### Retrieve a specific patient
```
GET /api/patients/{id}/
```
Response:
```json
{
  "ip_number": "string",
  "name": "string",
  "age": "integer",
  "sex": "string",
  "department": "string",
  "history": "string"
}
```

#### Update a specific patient
```
PUT /api/patients/{id}/
```
Request Body:
```json
{
  "ip_number": "string",
  "name": "string",
  "age": "integer",
  "sex": "string",
  "department": "string",
  "history": "string"
}
```
Response:
```json
{
  "ip_number": "string",
  "name": "string",
  "age": "integer",
  "sex": "string",
  "department": "string",
  "history": "string"
}
```

#### Delete a specific patient
```
DELETE /api/patients/{id}/
```
Response:
```
204 No Content
