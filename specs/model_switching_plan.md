# Model Switching Implementation Plan

## Overview
Add a command that allows dynamic switching between Claude models (Opus 4.6, Sonnet 4.5, and Haiku 4.5) during agent operation.

## Current State Analysis
Since this appears to be a fresh implementation, we'll need to:
1. Establish where model configuration is stored
2. Create a model switching mechanism
3. Add a user command interface

## Implementation Plan

### 1. Model Configuration Structure

Create a centralized model configuration system:

**File: `config/models.py`**
```python
from enum import Enum
from dataclasses import dataclass

class ModelType(Enum):
    OPUS = "claude-opus-4-20250514"
    SONNET = "claude-sonnet-4-20250514"
    HAIKU = "claude-haiku-4-20250514"

@dataclass
class ModelConfig:
    name: str
    model_id: str
    max_tokens: int
    temperature: float = 1.0
    
    @property
    def display_name(self):
        return self.name.split('-')[1].title()

AVAILABLE_MODELS = {
    'opus': ModelConfig(
        name='opus-4.6',
        model_id=ModelType.OPUS.value,
        max_tokens=8192
    ),
    'sonnet': ModelConfig(
        name='sonnet-4.5',
        model_id=ModelType.SONNET.value,
        max_tokens=8192
    ),
    'haiku': ModelConfig(
        name='haiku-4.5',
        model_id=ModelType.HAIKU.value,
        max_tokens=8192
    )
}

DEFAULT_MODEL = 'sonnet'
```

### 2. Modify Agent Class

**File: `core/model_manager.py`**
```python
class ModelManager:
    def __init__(self, default_model='sonnet'):
        self.current_model = default_model
        self.model_history = []
        
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        if model_name.lower() not in AVAILABLE_MODELS:
            return False
        
        self.model_history.append({
            'from': self.current_model,
            'to': model_name.lower(),
            'timestamp': datetime.now()
        })
        self.current_model = model_name.lower()
        return True
    
    def get_current_config(self) -> ModelConfig:
        """Get current model configuration"""
        return AVAILABLE_MODELS[self.current_model]
    
    def get_model_info(self) -> dict:
        """Return current model information"""
        config = self.get_current_config()
        return {
            'name': config.display_name,
            'model_id': config.model_id,
            'max_tokens': config.max_tokens
        }
```

### 3. Add Command to CommandProcessor

Add a special command that users can invoke to switch models:

**Command Format Options:**

1. **Natural language style:**
   - "switch to opus"
   - "use haiku model"
   - "change model to sonnet"

2. **Explicit command style:**
   - `/model opus`
   - `/switch sonnet`
   - `/use haiku`

**Implementation in agent loop:**

```python
def parse_user_command(user_input: str) -> tuple[str, str]:
    """Parse user input for special commands"""
    # Check for explicit commands
    if user_input.startswith('/model ') or user_input.startswith('/switch '):
        parts = user_input.split(maxsplit=1)
        if len(parts) == 2:
            return ('switch_model', parts[1].strip().lower())
    
    # Check for natural language commands
    switch_patterns = [
        r'switch to (\w+)',
        r'use (\w+) model',
        r'change model to (\w+)',
        r'set model to (\w+)'
    ]
    
    for pattern in switch_patterns:
        match = re.match(pattern, user_input.lower())
        if match:
            return ('switch_model', match.group(1))
    
    return ('normal', user_input)
```

### 4. Integration Points

#### A. Agent Initialization
```python
def __init__(self):
    self.model_manager = ModelManager(default_model='sonnet')
    self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

#### B. Message Processing
```python
def send_message(self, messages: list) -> str:
    config = self.model_manager.get_current_config()
    
    response = self.anthropic_client.messages.create(
        model=config.model_id,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        messages=messages
    )
    
    return response.content[0].text
```

#### C. Command Handling
```python
def handle_user_input(self, user_input: str):
    cmd_type, content = parse_user_command(user_input)
    
    if cmd_type == 'switch_model':
        if self.model_manager.switch_model(content):
            info = self.model_manager.get_model_info()
            return f"✓ Switched to {info['name']} ({info['model_id']})"
        else:
            return f"✗ Unknown model: {content}. Available: opus, sonnet, haiku"
    
    # Normal message processing
    return self.process_message(content)
```

### 5. User Feedback

When model switches occur, provide clear feedback:

```
User: /model opus
Agent: ✓ Switched to Opus (claude-opus-4-20250514)
      Max tokens: 8192 | Temperature: 1.0

User: switch to haiku
Agent: ✓ Switched to Haiku (claude-haiku-4-20250514)
      Max tokens: 8192 | Temperature: 1.0
      Note: Haiku is optimized for speed and cost efficiency.

User: /model invalid
Agent: ✗ Unknown model: invalid
      Available models:
      - opus: Claude Opus 4.6 (most capable)
      - sonnet: Claude Sonnet 4.5 (balanced)
      - haiku: Claude Haiku 4.5 (fast & efficient)
```

### 6. Persistence (Optional)

Store model preference between sessions:

**File: `config/preferences.json`**
```json
{
    "default_model": "sonnet",
    "last_used": "opus",
    "model_usage_stats": {
        "opus": {"count": 15, "last_used": "2025-01-20T10:30:00"},
        "sonnet": {"count": 43, "last_used": "2025-01-20T11:45:00"},
        "haiku": {"count": 8, "last_used": "2025-01-19T09:15:00"}
    }
}
```

### 7. Testing Strategy

Create tests for:
1. Model switching validation
2. Invalid model names
3. Model configuration retrieval
4. Command parsing (both formats)
5. Persistence (if implemented)

**File: `tests/test_model_switching.py`**
```python
def test_switch_to_valid_model():
    manager = ModelManager()
    assert manager.switch_model('opus') == True
    assert manager.current_model == 'opus'

def test_switch_to_invalid_model():
    manager = ModelManager()
    assert manager.switch_model('gpt4') == False
    
def test_command_parsing():
    assert parse_user_command('/model opus') == ('switch_model', 'opus')
    assert parse_user_command('switch to haiku') == ('switch_model', 'haiku')
```

## Implementation Order

1. **Phase 1:** Create model configuration (config/models.py)
2. **Phase 2:** Implement ModelManager (core/model_manager.py)
3. **Phase 3:** Add command parsing to agent
4. **Phase 4:** Integrate with API calls
5. **Phase 5:** Add user feedback messages
6. **Phase 6:** (Optional) Add persistence
7. **Phase 7:** Write tests

## Benefits

- **Flexibility:** Switch models based on task complexity
- **Cost optimization:** Use Haiku for simple tasks, Opus for complex ones
- **Easy testing:** Compare model behaviors on same prompts
- **User control:** Let users choose their preferred model

## Future Enhancements

1. **Auto-switching:** Automatically select model based on task complexity
2. **Cost tracking:** Track API costs per model
3. **Performance metrics:** Compare response times and quality
4. **Model presets:** Save custom configurations for specific workflows
5. **Fallback mechanism:** Auto-fallback to different model if one fails

## Files to Create/Modify

- `config/models.py` (new)
- `core/model_manager.py` (new)
- `agent.py` or `main.py` (modify - add command parsing and integration)
- `tests/test_model_switching.py` (new)
- `specs/model_switching_plan.md` (this file)

## Estimated Effort

- Core implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes
- Total: 3.5-4.5 hours