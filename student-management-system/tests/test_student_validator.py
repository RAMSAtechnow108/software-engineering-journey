from validators.student_validator import StudentValidator
import pytest
from exceptions.validation_exceptions import InvalidAgeError



def test_valid_age():
    result =StudentValidator.validate_age("21")

    assert result==21


def test_invalid_age_raises_error():
    with pytest.raises(InvalidAgeError) as info:
        StudentValidator.validate_age("15")
    
    print(info.value)

def test_non_numeric_age_raises_error():
    
    with pytest.raises(InvalidAgeError) as exc_info:
        StudentValidator.validate_age("abd")
        
    print(exc_info.value)