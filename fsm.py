import os
from collections import defaultdict

class FiniteStateMachine(object):
    """A class representing a finite state machine.
    
    A finite state machine (FSM) can be initialized from a CSV file formatted 
    as follows:
    
    Line #      Description
    -----------------------
    0                States
    1               Symbols
    2         Initial State
    3       Terminal States
    4+          Transitions
    
    Example
    -----------------------
    0 : A,B,C
    1 : a,b
    2 : A
    3 : A,C
    4 : A,a,A
    5 : A,b,B
    6 : B,a,C
    7 : B,b,C
    8 : C,a,C
    9 : C,b,A"""
    
    def __init__(self, file):
        super(FiniteStateMachine, self).__init__()
        self.records = map(lambda l : l.strip().split(','), file.readlines())
        self.parse(self.records)
        self.reset()
    
    def __repr__(self):
        labels = [
            'States',
            'Symbols',
            'Initial State',
            'Terminal States',
            'Transitions',
            'Current State'
        ]
        data = [
            ', '.join(sorted(self.states)),    # States
            ', '.join(sorted(self.symbols)),   # Symbols
            self.initial_state,                # Initial State
            ', '.join(sorted(self.terminals)), # Terminal States
            '\n\t'.join([''] + [
                "'{s}' : {m}".format(s=state, m=mapping)
                for state, mapping in sorted(self.transitions.items())
            ]),                                # Transitions
            self.current_state                 # Current State
        ]
        labeled_data = [
            '{l} : {d}'.format(l=label, d=data)
            for label, data in zip(labels, data)
        ]
        return '\n'.join(labeled_data)
    
    def parse(self, records):
        """Parses a CSV file to set up the FSM."""
        self.states = set(records[0])
        self.symbols = set(records[1])
        self.initial_state = records[2][0]
        self.terminals = set(records[3])
        self.transitions = defaultdict(dict)
        # Iterate over the defined transitions
        for from_state, symbol, to_state in records[4:]:
            # Validate each transition
            self.validate_transition(from_state, to_state)
            # Populate the transitions dictionary
            self.transitions[from_state][symbol] = to_state
    
    def validate_transition(self, from_state, to_state):
        """Raises an error if an invalid transition is given."""
        invalid_states = set([from_state, to_state]).difference(self.states)
        if invalid_states:
            raise StateError(', '.join(sorted(invalid_states)))
    
    def reset(self):
        """Resets the current state to the initial state."""
        self.current_state = self.initial_state
    
    def advance(self, symbol):
        """Transitions the FSM to the next state given a symbol."""
        # Ensure the symbol is licensed by the FSM before advancing
        if symbol not in self.symbols:
            raise SymbolError(symbol)
        from_state = self.current_state
        to_state = self.transitions[from_state].get(symbol)
        # Format a human readable string representation of the transition
        transition = '{f} -{s}-> {t}'.format(f=from_state, s=symbol, t=to_state)
        if to_state:
            # If the transition is valid, update the state
            print(transition)
            self.current_state = to_state
        else:
            # Otherwise the state being transitioned to is invalid
            raise TransitionError(transition)
    
    def run(self, sequence):
        """Advances the state of the FSM by iterating over a symbol sequence."""
        # Ensure we start the sequence from the initial state
        self.reset()
        print("Running sequence : '{s}'".format(s=sequence))
        # Iterate over the sequence
        map(self.advance, sequence)
        # Check whether the sequence finished at a terminal or not
        is_terminated = True if self.current_state in self.terminals else False
        # Print a termination status message
        if is_terminated:
            print('Terminated')
        else:
            print('Failed to terminate')

class TransitionError(RuntimeError):
    """An exception to be raised when an illegal transition is encountered."""
    def __init__(self, transition):
        super(TransitionError, self).__init__(transition)

class StateError(RuntimeError):
    """An exception to be raised if a transition references an invalid state."""
    def __init__(self, state):
        super(StateError, self).__init__(state)

class SymbolError(RuntimeError):
    """An exception to be raised when a sequence includes an invalid symbol."""
    def __init__(self, symbol):
        super(SymbolError, self).__init__(symbol)

if __name__ == '__main__':
    with open('fsm_test.csv', 'r') as file:
        fsm = FiniteStateMachine(file)
    sequence1 = 'abbaabab'
    sequence2 = 'abbaab'
    print(fsm)
    fsm.run(sequence1)
    fsm.run(sequence2)