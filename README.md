# Diet Planner Backend

## API Documentation

`GET /api/status` - Returns the status of the API  
`POST /api/users/login` - Logs in the user and sets a jwt token  
`POST /api/users/register` - Registers the user and redirects to login page  
`GET /api/users/{user_id}` - Returns the basic user data  
`PUT /api/users/{user_id}` - To update the user data  
`GET /api/users/{user_id}/diet_plans` - Returns the generated diet plans of the user  
`POST /api/users/{user_id}/generate_diet_plan` - Generates a diet plan for the user  
