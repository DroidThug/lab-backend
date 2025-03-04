# Lab Requisition System

This project is a Lab Requisition System built using Django. It allows users to manage lab orders and patient information.

## Features
- Manage lab orders
- Manage patient information
- REST API for integration with other systems

## Installation

1. Clone the repository:
```bash
$ git clone <repository-url>
```

2. Navigate to the project directory:
```bash
$ cd lab
```

3. Install the dependencies:
```bash
$ pip install -r requirements.txt
```

4. Set up the database:
```bash
$ python manage.py migrate
```

5. Run the development server:
```bash
$ python manage.py runserver
```

## Usage

- Access the admin panel at `http://localhost:8000/admin`
- Use the API endpoints to manage lab orders and patient information

## API Endpoints

- `GET /api/orders/orders/` - List all lab orders
- `POST /api/orders/orders/` - Create a new lab order
- `GET /api/orders/orders/{id}/` - Retrieve a specific lab order
- `PUT /api/orders/orders/{id}/` - Update a specific lab order
- `DELETE /api/orders/orders/{id}/` - Delete a specific lab order

- `GET /api/orders/tests/` - List all tests
- `POST /api/orders/tests/` - Create a new test
- `GET /api/orders/tests/{id}/` - Retrieve a specific test
- `PUT /api/orders/tests/{id}/` - Update a specific test
- `DELETE /api/orders/tests/{id}/` - Delete a specific test

- `GET /api/patients/` - List all patients
- `POST /api/patients/` - Create a new patient
- `GET /api/patients/{id}/` - Retrieve a specific patient
- `PUT /api/patients/{id}/` - Update a specific patient
- `DELETE /api/patients/{id}/` - Delete a specific patient

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License.
