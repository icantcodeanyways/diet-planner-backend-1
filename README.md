# Diet Planner Backend

## API Documentation

`GET /api/status` - Returns the status of the API  

`POST /api/users/login` - Logs in the user and returns a jwt token  

`POST /api/users/register` - Registers the user  

`GET /api/users/{user_id}` - Returns the basic user data  (protected)

`PATCH /api/users/{user_id}` - To update the user data  (protected)

`DELETE /api/users/{user_id}` - Delete user account (protected)

`GET /api/users/{user_id}/diet_plans` - Returns the generated diet plans of the user  (protected)

`POST /api/users/{user_id}/generate_diet_plan` - Generates a diet plan for the user (protected)
