
// Main.js - Global JavaScript functions

document.addEventListener('DOMContentLoaded', function() {
    // Handle flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            // Make flash messages dismissible
            message.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }, 5000);
        });
    }
    
    // Add responsive menu toggle for mobile
    const header = document.querySelector('header');
    if (header) {
        const navList = header.querySelector('nav ul');
        const logoDiv = header.querySelector('.logo');
        
        // Create hamburger menu icon for mobile
        const mobileMenuToggle = document.createElement('div');
        mobileMenuToggle.className = 'mobile-menu-toggle';
        mobileMenuToggle.innerHTML = '<span></span><span></span><span></span>';
        header.querySelector('.container').appendChild(mobileMenuToggle);
        
        // Style the toggle button
        const style = document.createElement('style');
        style.textContent = `
            .flash-message {
                padding: 10px 15px;
                margin-bottom: 15px;
                border-radius: 5px;
                cursor: pointer;
                position: relative;
                transition: opacity 0.3s ease;
            }
            .flash-message.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .flash-message.error, .flash-message.danger {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .flash-message.warning {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeeba;
            }
            .flash-message.info {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            
            @media (max-width: 768px) {
                nav ul {
                    display: none;
                    flex-direction: column;
                    width: 100%;
                }
                
                nav ul.show {
                    display: flex;
                }
                
                .mobile-menu-toggle {
                    display: flex;
                    flex-direction: column;
                    justify-content: space-around;
                    width: 30px;
                    height: 25px;
                    cursor: pointer;
                }
                
                .mobile-menu-toggle span {
                    display: block;
                    height: 3px;
                    width: 100%;
                    background-color: white;
                    border-radius: 3px;
                    transition: all 0.3s ease;
                }
                
                header .container {
                    position: relative;
                }
            }
            
            @media (min-width: 769px) {
                .mobile-menu-toggle {
                    display: none;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Toggle navigation on click
        mobileMenuToggle.addEventListener('click', () => {
            navList.classList.toggle('show');
        });
    }
});
