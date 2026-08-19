from pydantic import BaseModel, Field, validator

class Attendance(BaseModel):
    student_id: int = Field(..., description="Unique identifier for the student")
    student_name: str = Field(..., description="Name of the student")
    attendance_percentage: float = Field(..., description="Percentage of attendance")
    total_working_days: int = Field(..., description="Total number of working days")
    days_present: int = Field(..., description="Number of days present")
    days_absent: int = Field(..., description="Number of days absent")
    recent_attendance: list[bool] = Field(..., description="Recent attendance information (True for present, False for absent)")

    @validator('attendance_percentage')
    def validate_attendance_percentage(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError('Attendance percentage must be between 0.0 and 100.0')
        return v