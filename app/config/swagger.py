swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Chatbot API",
        "description": "API for chatbot",
        "contact": {
            "responsibleOrganization": "Chatbot",
            "responsibleDeveloper": "Chatbot",
            "email": "chatbot@chatbot.com",
            "url": "https://chatbot.com",
        },
        "version": "1.0",
    },
    "basePath": "/api/v1",  
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    "security": [{"Bearer": []}],
}