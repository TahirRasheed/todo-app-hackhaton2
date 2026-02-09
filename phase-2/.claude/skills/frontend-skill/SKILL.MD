---
name: frontend-skill
description: Build modern frontend pages, reusable components, layouts, and styling systems. Use for UI development.
---

# Frontend Page Builder Skill

## Instructions

1. **Page Structure**
   - Create responsive pages (Home, About, Dashboard, etc.)
   - Use semantic HTML structure
   - Implement proper spacing and sections

2. **Component Development**
   - Build reusable UI components
   - Examples: Navbar, Sidebar, Cards, Modals, Forms
   - Follow component-based architecture

3. **Layout System**
   - Use Flexbox and Grid
   - Create responsive layouts
   - Implement header, footer, and content areas

4. **Styling**
   - Use Tailwind CSS / CSS Modules / Styled Components
   - Maintain design consistency
   - Apply typography, colors, and spacing system

5. **Responsiveness**
   - Mobile-first design
   - Tablet and desktop breakpoints
   - Adaptive navigation (hamburger menu, collapsible sidebar)

---

## Best Practices

- Keep components small and reusable
- Maintain consistent spacing scale
- Use design tokens (colors, fonts, sizes)
- Avoid inline styles
- Ensure accessibility (ARIA labels, contrast)
- Optimize for performance

---

## Example Structure

```html
<div class="page-layout">
  
  <!-- Navbar -->
  <header class="navbar">
    <h1 class="logo">App Name</h1>
    <nav class="nav-links">
      <a href="#">Home</a>
      <a href="#">About</a>
      <a href="#">Contact</a>
    </nav>
  </header>

  <!-- Main Content -->
  <main class="content">
    <section class="card">
      <h2>Page Title</h2>
      <p>This is a reusable card component.</p>
      <button class="primary-btn">Action</button>
    </section>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <p>© 2026 Your Company</p>
  </footer>

</div>