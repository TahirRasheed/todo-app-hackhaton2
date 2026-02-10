// T018: Form Validation Utilities

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  return { isValid: true };
}

export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'Password is required' };
  }

  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters' };
  }

  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);

  if (!hasUppercase || !hasLowercase || !hasNumber) {
    return {
      isValid: false,
      error: 'Password must contain uppercase, lowercase, and number',
    };
  }

  return { isValid: true };
}

export function validateTaskTitle(title: string): ValidationResult {
  if (!title || title.trim() === '') {
    return { isValid: false, error: 'Title is required' };
  }

  if (title.length > 255) {
    return { isValid: false, error: 'Title must be 255 characters or less' };
  }

  return { isValid: true };
}

export function validateDescription(description: string): ValidationResult {
  if (description && description.length > 1000) {
    return { isValid: false, error: 'Description must be 1000 characters or less' };
  }

  return { isValid: true };
}

export function validateName(name: string): ValidationResult {
  if (!name || name.trim() === '') {
    return { isValid: false, error: 'Name is required' };
  }

  if (name.length > 255) {
    return { isValid: false, error: 'Name must be 255 characters or less' };
  }

  return { isValid: true };
}
