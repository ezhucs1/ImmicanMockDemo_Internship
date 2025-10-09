# How to Set Your Custom Background Image

## Method 1: Using a Local Image File (Recommended)

1. **Add your image to the public folder:**
   - Place your image file in: `frontend-react/public/`
   - Name it `background.jpg` (or change the filename in App.jsx)
   - Supported formats: JPG, PNG, WebP

2. **Update the image path in App.jsx:**
   ```jsx
   style={{backgroundImage: 'url(/your-image-name.jpg)'}}
   ```

## Method 2: Using an Online Image URL

Replace the background image URL in App.jsx:
```jsx
style={{backgroundImage: 'url(https://example.com/your-image.jpg)'}}
```

## Method 3: Multiple Background Options

You can easily switch between different backgrounds by changing the CSS class:

### Available Overlay Styles:
- `background-overlay` - Dark overlay (current)
- `background-overlay-light` - Light overlay
- `background-overlay-gradient` - Gradient overlay

### Example:
```jsx
// For a light overlay
<div className="absolute inset-0 background-overlay-light"></div>

// For a gradient overlay
<div className="absolute inset-0 background-overlay-gradient"></div>
```

## Background Image Tips:

1. **Image Size:** Use images at least 1920x1080 for best quality
2. **File Size:** Keep under 2MB for fast loading
3. **Aspect Ratio:** 16:9 or 4:3 work best
4. **Content:** Choose images that don't interfere with text readability

## Fallback:
If no image is found, the app will show a gradient background as fallback.

## Quick Test:
1. Add any image to `public/background.jpg`
2. Refresh your app
3. Your custom background should appear!


