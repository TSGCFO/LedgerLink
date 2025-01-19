
import { AppState } from './appState.js';
import { ThemeManager } from './main.js';
import { Toast } from './main.js';
import { Modal } from './main.js';
import { FormHandler } from './main.js';

  document.addEventListener('DOMContentLoaded', () => {
    'use strict';
    // Initialize AppState and ThemeManager
    ThemeManager.init();

    // Initialize forms with FormHandler
    document.querySelectorAll('form').forEach((form) => new FormHandler(form));

    // Example: Using Toast globally
    Toast.show('Welcome!', 'info');

    // Example: Modal usage (custom initialization, if needed)
    document.querySelectorAll('[data-modal-trigger]').forEach((trigger) => {
        trigger.addEventListener('click', () => {
            Modal.show({
                title: 'Example Modal',
                content: 'This is a modal example.',
            });
        });
    });
});
export { Toast, Modal, FormHandler };
