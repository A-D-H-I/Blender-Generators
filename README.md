# Blender Vehicle Parts Generator
Two powerful add-ons for creating mechanical components

## Included Add-ons

### 1. Gear Generator
⚙️ Creates parametric gears with real-time updates

Features:
- Live preview while adjusting parameters
- Customizable teeth count, radius, thickness
- Automatic beveling and smooth shading
- Non-destructive workflow

### 2. Wheel Generator
🛞 Produces realistic wheels with rims and tires

Features:
- Adjustable rim radius and width
- Customizable spoke count (0 for solid wheels)
- Automatic material assignment:
  - Rubber texture for tires
  - Metallic finish for rims/spokes
- Realistic tire tread pattern

## Installation

1. Download both add-ons:
   - `gear_generator.py`
   - `wheel_generator.py` (or `wheelgen.zip`)

2. In Blender:
   - Go to `Edit > Preferences > Add-ons > Install...`
   - Select one add-on at a time
   - Enable after installation

3. Repeat for the second add-on

## Usage

### Gear Generator
1. Open sidebar (`N` key)
2. Navigate to **Create** tab
3. Adjust parameters → changes happen live
4. Click "Add Gear"

### Wheel Generator
1. Find in `Add > Mesh > Wheel`
2. Customize in the operator panel:
   - Rim/tire dimensions
   - Spoke count (set to 0 for solid rims)
   - Material presets

## Technical Details

| Feature              | Gear Generator | Wheel Generator |
|----------------------|---------------|----------------|
| Real-time updates    | ✅ Yes         | ✅ No (regenerates) |
| Materials            | ✅ No          | ✅ Automatic textures |
| Modifier support     | ✅ Bevel       | ✅ Subdivision surface |
| Blender versions     | 2.83+         | 2.80+          |

## License
MIT License - Free for all uses

## Tips
- Combine both add-ons to create drivetrain systems
- Use Wheel Generator's metallic materials with Eevee/Cycles
- Parent gears to wheel empties for vehicle setups