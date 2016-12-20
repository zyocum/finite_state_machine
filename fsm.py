#!/usr/bin/env python3
__author__ = "Zachary Yocum"
__email__  = "zyocum@brandeis.edu"

"""A simple implementation of a finite state machine."""

import csv
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
    
    def __init__(self, filename):
        super(FiniteStateMachine, self).__init__()
        self.filename = filename
        try:
            self.parse(self.filename)
        except StateError as e:
            print(e)
        finally:
            self.reset()
    
    def __str__(self):
        return '\n'.join([
            'States: {}'.format(sorted(self.states)),
            'Symbols: {}'.format(sorted(self.symbols)),
            'Initial State: {}'.format(self.initial_state),
            'Terminal States: {}'.format(sorted(self.terminals)),
            'Transitions:\n\t{}'.format(
                '\n\t'.join('{} -> {}'.format(*t) for t in self.transitions.items())
            ),
            'Current State: {}'.format(self.current_state)
        ])
    
    def load_rows(self, filename):
        with open(filename, mode='r') as f:
            reader = csv.reader(f)
            for row in reader:
                yield row
    
    def parse(self, filename):
        """Parses a CSV file to initialize the FSM."""
        rows = list(self.load_rows(filename))
        self.states = set(rows[0])
        self.symbols = set(rows[1])
        self.initial_state = rows[2][0]
        self.terminals = set(rows[3])
        self.transitions = defaultdict(dict)
        for from_state, symbol, to_state in rows[4:]:
            self.validate_transition(from_state, to_state)
            self.transitions[from_state][symbol] = to_state
    
    def validate_transition(self, from_state, to_state):
        """Raises an error if an invalid transition is given."""
        invalid_states = {from_state, to_state}.difference(self.states)
        if invalid_states:
            raise StateError(invalid_states)
    
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
        print(transition)
        if to_state is None:
            raise TransitionError(transition)
        self.current_state = to_state
            
    
    def run(self, sequence):
        """Advances the state of the FSM by iterating over a symbol sequence."""
        self.reset()
        print("Running sequence : {}".format(sequence))
        try:
            for symbol in sequence:
                self.advance(symbol)
        except TransitionError as e:
            print(e)
        finally:
            if self.current_state in self.terminals:
                message = 'Terminated'
            else:
                message = 'Failed to terminate'
            print(message)

class TransitionError(ValueError):
    """An exception to be raised if an illegal transition is encountered."""
    def __init__(self, transition):
        message = 'Illegal transition encountered: {}'
        super(TransitionError, self).__init__(message.format(transition))

class StateError(ValueError):
    """An exception to be raised if a transition references an invalid state."""
    def __init__(self, states):
        message = 'Undefined state(s) encountered: {}'
        super(StateError, self).__init__(message.format(states))

class SymbolError(ValueError):
    """An exception to be raised if a sequence references an invalid symbol."""
    def __init__(self, symbol):
        message = 'Undefined symbol encountered: {}'
        super(SymbolError, self).__init__(message.format(symbol))

if __name__ == '__main__':
    fsm = FiniteStateMachine('fsm_test.csv')
    print(fsm)
    sequences = [
        'abbaabab',
        'abbaab',
        'abc'
    ]
    for i, sequence in enumerate(sequences, 1):
        print('Sequence {}:'.format(i))
        try:
            fsm.run(sequence)
        except Exception as e:
            print(e)
