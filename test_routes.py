# -*- coding: utf-8 -*-
"""
Pruebas Unitarias - PharmaSafe Analytics
Verifica que las rutas clave del controlador Flask carguen correctamente.
"""

import unittest
from app import app

class TestPharmaSafeRoutes(unittest.TestCase):
    def setUp(self):
        # Configurar el cliente de pruebas de Flask
        self.app = app.test_client()
        self.app.testing = True

    def test_redireccion_raiz(self):
        """Verifica que la raíz '/' redireccione correctamente a '/inicio'."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/inicio', response.headers.get('Location', ''))

    def test_paginas_principales(self):
        """Verifica que todas las vistas carguen con código HTTP 200."""
        paginas = [
            '/inicio', 
            '/dashboard', 
            '/incidentes', 
            '/riesgos', 
            '/cruce', 
            '/calidad', 
            '/hallazgos'
        ]
        for ruta in paginas:
            with self.subTest(ruta=ruta):
                response = self.app.get(ruta)
                self.assertEqual(response.status_code, 200, f"La ruta {ruta} falló con código {response.status_code}")

    def test_ruta_inexistente(self):
        """Verifica que las páginas no encontradas devuelvan código HTTP 404."""
        response = self.app.get('/ruta-inexistente-aleatoria')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
