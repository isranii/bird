# 🐦 Flappy Bird for Kids 🌟

A kid-friendly reimagining of the classic Flappy Bird game with enhanced gameplay mechanics and visual effects.

## ✨ Features

- **🎮 Kid-Friendly Gameplay**: Reduced gravity, larger pipe gaps, and forgiving collision detection
- **🌦️ Dynamic Weather System**: Rain, snow, and fog effects that impact gameplay
- **🍂 Seasonal Changes**: Four seasons with unique visual themes and gameplay modifiers
- **⚡ Power-Up System**: Collectible stars (bonus points) and shields (temporary invincibility)
- **🌅 Day/Night Cycle**: Dynamic sky colors and lighting based on score progression
- **✨ Particle Effects**: Visual feedback for scoring and power-up collection
- **📊 Score Tracking**: High score persistence and game statistics

## 🚀 Requirements

```bash
pip install pygame
```

## 🎯 Quick Start

```python
python flappy_bird.py
```

**🎮 Controls**: Press `SPACE` to jump/flap and restart after game over.

## 🎲 Game Mechanics

### Season 🌸

| Season | Gravity Modifier | Special Effect |
|--------|------------------|----------------|
| Spring 🌱 | -10% gravity | Easier gameplay |
| Summer ☀️ | -20% gravity | Extra easy mode |
| Fall 🍁 | Normal gravity | Standard difficulty |
| Winter ❄️ | +10% gravity | 2x score multiplier |

### Weather 🌤️

| Weather | Visual Effect | Gameplay Impact |
|---------|---------------|-----------------|
| Rain 🌧️ | Animated raindrops | Slight wind effects |
| Snow ❄️ | Falling snowflakes | Reduced gravity |
| Fog 🌫️ | Translucent overlay | 3x score multiplier |

## 🎁 Power-Ups

- **⭐ Star**: +5 bonus points with particle explosion
- **🛡️ Shield**: 5 seconds of invincibility
```