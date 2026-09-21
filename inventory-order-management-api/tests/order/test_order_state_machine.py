from app.constants.order_constants import OrderStatus
from app.domain.order_state.state_machine import OrderStateMachine
import pytest
from app.exceptions.order_exceptions import InvalidOrderStatusTransitionError

def test_valid_order_transitions():
    
    OrderStateMachine.validate_transition(
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED
    )

    
    OrderStateMachine.validate_transition(
        OrderStatus.PENDING,
        OrderStatus.CANCELLED
    )


    OrderStateMachine.validate_transition(
        OrderStatus.PENDING,
        
        OrderStatus.EXPIRED
    )
    
    
    OrderStateMachine.validate_transition(
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED
    )
    


def test_invalid_order_transitions():
    
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.PENDING,
            OrderStatus.SHIPPED
        )
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.PENDING,
            OrderStatus.SHIPPED
        )
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.EXPIRED,
            OrderStatus.CONFIRMED
        )
        
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.CANCELLED,
            OrderStatus.SHIPPED
        )
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.CANCELLED,
            OrderStatus.SHIPPED
        )
        
    
    with pytest.raises(InvalidOrderStatusTransitionError):

        assert not OrderStateMachine.validate_transition(
            OrderStatus.DELIVERED,
            OrderStatus.PENDING
        )
        


def test_terminal_states_connot_transition():
    
    terminal_states = [
        OrderStatus.CANCELLED,
        OrderStatus.EXPIRED,
        OrderStatus.DELIVERED
    ]
    
    
    for status in terminal_states:
        
        with pytest.raises(InvalidOrderStatusTransitionError):
            assert not OrderStateMachine.validate_transition(
                status,OrderStatus.CONFIRMED
            )
            
        with pytest.raises(InvalidOrderStatusTransitionError):    
            assert not OrderStateMachine.validate_transition(
                status,OrderStatus.SHIPPED
            )
            
        with pytest.raises(InvalidOrderStatusTransitionError):    
            assert not OrderStateMachine.validate_transition(
                status,OrderStatus.DELIVERED
            )
        
        
        
        