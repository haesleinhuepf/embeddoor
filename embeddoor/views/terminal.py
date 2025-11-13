"""IPython terminal view module for embeddoor.

Provides an interactive IPython terminal for data exploration.
"""

from flask import jsonify, request, Response
import json
import sys
import os
import configparser
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

🤖 AI Assistant:
  Type "bob <your request>" to get AI-generated Python code
  Example: bob show first 10 rows sorted by price
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
    
    @app.route('/api/view/terminal/bob', methods=['POST'])
    def bob_assist():
        """Ask Bob (LLM assistant) to generate Python code.
        
        Request JSON:
            session_id: str - Session identifier
            prompt: str - User's natural language request
        
        Returns:
            JSON with suggested Python code
        """
        try:
            data = request.json
            session_id = data.get('session_id', 'default')
            prompt = data.get('prompt', '')
            
            if not prompt.strip():
                return jsonify({
                    'success': False,
                    'error': 'Empty prompt provided'
                }), 400
            
            # Get or create shell to gather context
            if session_id not in app.ipython_shells:
                init_terminal()
            
            shell = app.ipython_shells.get(session_id)
            
            # Gather information about available variables
            variables_info = []
            if shell:
                # Get user namespace variables (exclude built-ins and modules)
                for var_name, var_value in shell.user_ns.items():
                    if not var_name.startswith('_'):
                        var_type = type(var_value).__name__
                        
                        # Add more details for known types
                        details = ""
                        if var_type == 'DataFrame':
                            details = f" with shape {var_value.shape} and columns {list(var_value.columns)}"
                        elif var_type == 'ndarray':
                            details = f" with shape {var_value.shape}"
                        elif var_type in ['list', 'dict', 'tuple', 'set']:
                            details = f" with length {len(var_value)}"
                        
                        variables_info.append(f"  - {var_name}: {var_type}{details}")
            
            variables_context = "\n".join(variables_info) if variables_info else "  No variables defined yet"
            
            # Read LLM configuration
            config = configparser.ConfigParser()
            config_path = os.path.join(os.getcwd(), 'config.ini')
            
            # Default values
            llm_api_url = "https://llm.scads.ai/v1/chat/completions"
            llm_api_key = None
            llm_model = "openai/gpt-oss-120b"
            
            if os.path.exists(config_path):
                config.read(config_path)
                if 'llm' in config:
                    llm_api_url = config['llm'].get('llm_api_url', llm_api_url)
                    llm_api_key = config['llm'].get('llm_api_key', None)
                    llm_model = config['llm'].get('llm_model', llm_model)
            
            # Read API key from environment variable if not set in config
            if not llm_api_key:
                llm_api_key = os.environ.get('SCADSAI_API_KEY', os.environ.get('OPENAI_API_KEY', 'ollama'))
            
            # Construct prompt for LLM
            system_prompt = """You are a Python code assistant. The user is working in an IPython terminal with data analysis tools.
Your task is to generate a SINGLE LINE of Python code that accomplishes what the user asks.

Available variables in the current session:
{variables_context}

Important:
- Return ONLY the Python code, no explanations or markdown
- Make it a single line (you can use semicolons to chain commands if needed)
- Use the available variables when appropriate
- Common imports are available: pandas as pd, numpy as np
- The main DataFrame is typically in variable 'data'
- Keep it concise and executable"""
            
            full_prompt = system_prompt.format(variables_context=variables_context)
            
            # Call LLM API
            import requests
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            if llm_api_key and llm_api_key.lower() != 'none':
                headers['Authorization'] = f'Bearer {llm_api_key}'
            
            llm_payload = {
                'model': llm_model,
                'messages': [
                    {'role': 'system', 'content': full_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 200
            }
            
            llm_response = requests.post(
                llm_api_url,
                headers=headers,
                json=llm_payload,
                timeout=30
            )
            
            if llm_response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f'LLM API error: {llm_response.status_code} - {llm_response.text}'
                }), 500
            
            llm_result = llm_response.json()
            
            # Extract the generated code
            suggested_code = llm_result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            # Clean up the code (remove markdown code blocks if present)
            if suggested_code.startswith('```'):
                lines = suggested_code.split('\n')
                suggested_code = '\n'.join(lines[1:-1]) if len(lines) > 2 else suggested_code
                suggested_code = suggested_code.replace('```python', '').replace('```', '').strip()
            
            return jsonify({
                'success': True,
                'code': suggested_code
            })
            
        except requests.RequestException as e:
            return jsonify({
                'success': False,
                'error': f'Error connecting to LLM server: {str(e)}'
            }), 500
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': f'Error processing Bob request: {traceback.format_exc()}'
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
