# El Explorador Submarino

**Videojuego 2D desarrollado en Python con Pygame**

Se trata de un juego de exploración submarina donde controlas a un valiente buzo que debe recolectar todas las perlas de un arrecife de coral laberíntico mientras evita a los peligrosos depredadores marinos.

## Información del Proyecto

- **Lenguaje**: Python 3.13.3
- **Framework**: Pygame 2.6.1
- **Librerías adicionales**: NumPy (para cálculos matemáticos optimizados)
- **Tipo**: Videojuego 2D de exploración y supervivencia
- **Género**: Aventura/Laberinto
- **Desarrollado por**: [Nayeli Noemi Cruz Angulo, Iber Javier Caicedo Ortiz]
- **Fecha**: 2025

## Descripción del Juego

### Concepto Original
"El Explorador Submarino" es un juego único que combina exploración de laberintos con supervivencia submarina. El jugador controla a un buzo profesional que debe explorar un arrecife de coral generado proceduralmente para recolectar valiosas perlas mientras evita a tiburones agresivos y medusas venenosas.

### Historia
Como explorador submarino experto, has descubierto un arrecife de coral legendario lleno de perlas preciosas. Sin embargo, este ecosistema está protegido por peligrosos depredadores marinos. Tu misión es recolectar todas las perlas usando tu experiencia, agilidad y las herramientas de supervivencia disponibles.

## Mecánicas del Juego

### Mecánicas Principales Implementadas

#### 1. **Exploración de Laberinto**
- Navegación en un arrecife de coral generado proceduralmente
- Laberinto único en cada partida usando algoritmo de división recursiva
- Múltiples rutas y callejones sin salida para aumentar la complejidad

#### 2. **Sistema de Recolección**
- **Perlas Blancas**: Recolectables básicos (+10 puntos cada una)
- **Perlas Gigantes Doradas**: Recolectables especiales (+50 puntos + arpón temporal)
- Sistema de inventario automático con contador visual

#### 3. **Sistema de Supervivencia**
- **3 vidas** del jugador con sistema de invulnerabilidad temporal
- **Enemigos inteligentes** con IA de patrullaje y persecución
- **Arpón temporal** como herramienta de supervivencia (ahuyenta enemigos por 5 segundos)

#### 4. **Sistema de Puntuación Avanzado**
- Puntuación base por recolección de perlas
- Bonus por completar nivel (+1000 puntos)
- Bonus por vidas restantes (+200 por vida)
- **Guardado automático** de mejores puntuaciones en archivo JSON

#### 5. **Inteligencia Artificial**
- **IA de Tiburones**: Patrullaje territorial, persecución y evasión del arpón
- **IA de Medusas**: Movimiento errático y reacción al arpón
- **Sistema anti-atascamiento** para enemigos
- **Generación procedural** inteligente del laberinto

#### 6. **Sistema de Efectos Visuales**
- **Motor de partículas** completo (burbujas, explosiones, destellos)
- **Animaciones fluidas** para todos los personajes
- **Screen shake** en eventos importantes
- **Gradientes de agua** y efectos de profundidad

## Controles del Juego

### Controles Principales
| Tecla | Función | Descripción |
|-------|---------|-------------|
| `W` `A` `S` `D` | Movimiento | Mover buzo en 4 direcciones |
| `↑` `↓` `←` `→` | Movimiento | Alternativa con flechas |
| `ESPACIO` | Acción principal | Iniciar juego / Continuar |
| `ESC` | Pausa/Salir | Pausar juego o salir |

### Controles de Menú
| Tecla | Función |
|-------|---------|
| `I` | Ver instrucciones detalladas |
| `H` | Ver tabla de puntuaciones |
| `R` | Reiniciar partida (en Game Over) |
| `M` | Volver al menú principal (en pausa) |

### Dependencias Requeridas
```bash
pygame>=2.0.0
numpy>=1.19.0

## Créditos y Atribuciones

Este proyecto fue desarrollado como parte del proyecto final de Estructuras de datos en el tercer ciclo de Ingeniería en Tecnologías de la Información.