const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 80;
const DATA_FILE = path.join(__dirname, 'contacts.json');

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

// Servir el frontend de forma estática
app.use(express.static(path.join(__dirname, 'frontend')));

// Inicializar base de datos local si no existe
function getContacts() {
  if (!fs.existsSync(DATA_FILE)) {
    const initial = [
      {
        id: "1",
        nombre: "Ing. Jaime Farfán",
        telefono: "+51 987 654 321",
        email: "jfarfan@tecsup.edu.pe",
        empresa: "Docente Cloud Computing",
        categoria: "VIP",
        favorito: true,
        notas: "Docente de Desarrollo de Soluciones en la Nube"
      },
      {
        id: "2",
        nombre: "Anderson Silva",
        telefono: "+51 912 345 678",
        email: "anderson@cloud.pe",
        empresa: "Estudiante C24 - DevOps",
        categoria: "Trabajo",
        favorito: true,
        notas: "Arquitecto de la solución en AWS EC2"
      },
      {
        id: "3",
        nombre: "Soporte AWS Cloud",
        telefono: "+1 800 123 4567",
        email: "aws-support@amazon.com",
        empresa: "Amazon Web Services",
        categoria: "Trabajo",
        favorito: false,
        notas: "Monitoreo de instancias EC2"
      }
    ];
    fs.writeFileSync(DATA_FILE, JSON.stringify(initial, null, 2));
    return initial;
  }
  return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
}

function saveContacts(contacts) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(contacts, null, 2));
}

// 1. Healthcheck para AWS
app.get('/health', (req, res) => {
  res.json({
    status: 'ONLINE',
    os: process.platform,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// 2. Listar y buscar contactos
app.get('/api/contacts', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  let contacts = getContacts();

  if (q) {
    contacts = contacts.filter(c =>
      (c.nombre && c.nombre.toLowerCase().includes(q)) ||
      (c.email && c.email.toLowerCase().includes(q)) ||
      (c.telefono && c.telefono.includes(q)) ||
      (c.empresa && c.empresa.toLowerCase().includes(q))
    );
  }

  res.json({ total: contacts.length, contacts });
});

// 2.1 Obtener contacto por ID
app.get('/api/contacts/:id', (req, res) => {
  const { id } = req.params;
  const contacts = getContacts();
  const contact = contacts.find(c => c.id === id);
  if (!contact) {
    return res.status(404).json({ error: 'Contacto no encontrado' });
  }
  res.json(contact);
});

// 3. Crear contacto
app.post('/api/contacts', (req, res) => {
  const { nombre, telefono, email, empresa, categoria, notas, favorito } = req.body;
  if (!nombre || !telefono) {
    return res.status(400).json({ error: 'Nombre y teléfono son requeridos' });
  }

  const contacts = getContacts();
  const newContact = {
    id: Date.now().toString(),
    nombre,
    telefono,
    email: email || '',
    empresa: empresa || '',
    categoria: categoria || 'Personal',
    notas: notas || '',
    favorito: !!favorito,
    avatar_url: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(nombre)}`,
    created_at: new Date().toISOString()
  };

  contacts.unshift(newContact);
  saveContacts(contacts);
  res.status(201).json({ message: 'Contacto guardado con éxito', contact: newContact });
});

// 4. Modificar contacto
app.put('/api/contacts/:id', (req, res) => {
  const { id } = req.params;
  const contacts = getContacts();
  const index = contacts.findIndex(c => c.id === id);

  if (index === -1) {
    return res.status(404).json({ error: 'Contacto no encontrado' });
  }

  contacts[index] = { ...contacts[index], ...req.body, updated_at: new Date().toISOString() };
  saveContacts(contacts);
  res.json({ message: 'Contacto actualizado', contact: contacts[index] });
});

// 5. Eliminar contacto
app.delete('/api/contacts/:id', (req, res) => {
  const { id } = req.params;
  let contacts = getContacts();
  const initialLength = contacts.length;
  contacts = contacts.filter(c => c.id !== id);

  if (contacts.length === initialLength) {
    return res.status(404).json({ error: 'Contacto no encontrado' });
  }

  saveContacts(contacts);
  res.json({ message: 'Contacto eliminado correctamente', id });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Nexus Contacts Server corriendo en http://0.0.0.0:${PORT}`);
});
