"""IPython terminal view module for embeddoor.

Provides an interactive IPython terminal for data exploration.
"""

from flask import jsonify, request, Response
import json
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def register_terminal_routes(app):
    """Register terminal-related routes."""
    
    # Store IPython shell instances per session
    if not hasattr(app, 'ipython_shells'):
        app.ipython_shells = {}
    
    @app.route('/api/view/terminal/init', methods=['POST'])
    def init_terminal():
        """Initialize an IPython terminal session.
        
        Request JSON:
            session_id: str - Unique session identifier
        
        Returns:
            JSON with success status and welcome message
        """
        try:
            from IPython.terminal.embed import InteractiveShellEmbed
            from IPython.core.interactiveshell import InteractiveShell
            
            data = request.json or {}
            session_id = data.get('session_id', 'default')
            
            # Create IPython shell if not exists
            if session_id not in app.ipython_shells:
                # Create a new IPython shell
                shell = InteractiveShellEmbed()
                
                # Inject global variables
                shell.user_ns['data'] = app.data_manager.df
                shell.user_ns['viewer'] = app.data_manager
                shell.user_ns['pd'] = __import__('pandas')
                shell.user_ns['np'] = __import__('numpy')
                
                app.ipython_shells[session_id] = shell
                
                welcome_msg = """IPython Terminal Initialized
================================
Available variables:
  - data: Current DataFrame
  - viewer: DataManager instance
  - pd: pandas module
  - np: numpy module

Try: data.head(), data.describe(), data.shape
"""
                return jsonify({
                    'success': True,
                    'output': welcome_msg
                })
            else:
                return jsonify({
                    'success': True,
                    'output': 'Session already initialized.\n'
                })
                
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'IPython not installed. Please install with: pip install ipython'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error initializing terminal: {str(e)}'
            }), 500
    
    @app.route('/api/view/terminal/execute', methods=['POST'])
    def execute_code():
        """Execute code in the IPython terminal.
        
        Request JSON:
            session_id: str - Session identifier
            code: str - Python code to execute
        
        Returns:
            JSON with execution result (output and/or error)
        """
        try:
            data = request.json
            session_id = data.get('session_id', 'default')
            code = data.get('code', '')
            
            if not code.strip():
                return jsonify({
                    'success': True,
                    'output': '',
                    'error': ''
                })
            
            # Get or create shell
            if session_id not in app.ipython_shells:
                # Initialize if not exists
                init_result = init_terminal()
                if isinstance(init_result, tuple):  # Error response
                    return init_result
            
            shell = app.ipython_shells[session_id]
            
            # Update global variables in case data changed
            shell.user_ns['data'] = app.data_manager.df
            shell.user_ns['viewer'] = app.data_manager
            
            # Capture output
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            result = None
            error_occurred = False
            
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    result = shell.run_cell(code, store_history=True)
                
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
                
                # Check execution result
                if result.error_in_exec:
                    error_occurred = True
                    if result.error_in_exec:
                        # Get the exception info
                        import traceback
                        error += ''.join(traceback.format_exception(
                            type(result.error_in_exec),
                            result.error_in_exec,
                            result.error_in_exec.__traceback__
                        ))
                
                return jsonify({
                    'success': not error_occurred,
                    'output': output,
                    'error': error
                })
                
            except Exception as exec_error:
                import traceback
                error_msg = ''.join(traceback.format_exception(
                    type(exec_error), exec_error, exec_error.__traceback__
                ))
                return jsonify({
                    'success': False,
                    'output': stdout_capture.getvalue(),
                    'error': error_msg
                })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'output': '',
                'error': f'Execution error: {traceback.format_exc()}'
            }), 500
    
    @app.route('/api/view/terminal/complete', methods=['POST'])
    def get_completions():
        """Get code completions for the terminal.
        
        Request JSON:
            session_id: str - Session identifier
            code: str - Code context
            cursor_pos: int - Cursor position in code
        
        Returns:
            JSON with completion suggestions
        """
        try:
            data = request.json
            session_id = data.get('session_id', 'default')
            code = data.get('code', '')
            cursor_pos = data.get('cursor_pos', len(code))
            
            if session_id not in app.ipython_shells:
                return jsonify({
                    'success': True,
                    'completions': []
                })
            
            shell = app.ipython_shells[session_id]
            
            # Get completions
            completions = shell.complete(code, cursor_pos)
            
            return jsonify({
                'success': True,
                'completions': completions[1] if completions else []
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'completions': []
            }), 500
    
    @app.route('/api/view/terminal/reset', methods=['POST'])
    def reset_terminal():
        """Reset the terminal session.
        
        Request JSON:
            session_id: str - Session identifier
        
        Returns:
            JSON with success status
        """
        try:
            data = request.json or {}
            session_id = data.get('session_id', 'default')
            
            if session_id in app.ipython_shells:
                del app.ipython_shells[session_id]
            
            return jsonify({
                'success': True,
                'output': 'Terminal reset.\n'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
