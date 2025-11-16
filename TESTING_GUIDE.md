# Testing Guide - Sistema de Chamada Automática

## 🚀 Quick Start Testing

Both servers are now running:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 📋 Test Sequence

### 1️⃣ Setup Phase (Admin Role)

#### Create Classes
1. Click **Admin** tab
2. Select **Criar Turmas**
3. Create test classes:
   - "Inteligência Artificial 1º Ano"
   - "Data Science 2º Ano"
   - "Ciência da Computação 3º Ano"

#### Register Professors
1. Go to **Registrar Professor**
2. Add professors:
   - Name: "Prof. Carlos Silva"
   - Email: "carlos@example.com"
   - Assign to: IA 1º Ano
3. Add more professors as needed

#### Register Students
1. Go to **Registrar Aluno**
2. Fill student information:
   - Name: "João Silva"
   - Select class from dropdown
   - Upload 2-3 photos of face (front, slight angles)
3. Wait for processing confirmation
4. Register 3-5 students for testing

---

### 2️⃣ Professor Validation Phase

#### Validate Students
1. Switch to **Professor** tab
2. Select **Validar Alunos**
3. Review pending students
4. Click **Validar** for each student
5. Verify status changes to "Validado"

---

### 3️⃣ Attendance Testing (Student Role)

#### Test Face Recognition (Test Mode)
1. Switch to **Aluno** tab
2. Check **Modo Teste** checkbox
3. Click **Iniciar Câmera**
4. Position face in camera
5. Click **Testar Reconhecimento**
6. Verify:
   - Face is recognized
   - Student name appears
   - Confidence score shown
   - "Modo Teste" warning displayed
   - NO attendance is registered

#### Register Real Attendance (Entry)
1. Uncheck **Modo Teste**
2. Click **Iniciar Câmera** (if stopped)
3. Click **Registrar Presença**
4. Verify:
   - "Entrada Registrada!" message
   - Student name displayed
   - Confidence and method shown
   - Attendance ID returned

#### Register Exit
1. Same student, without test mode
2. Click **Registrar Presença** again
3. Verify:
   - "Saída Registrada!" message
   - System automatically detected it's an exit
   - Different presenca_id

---

### 4️⃣ Attendance Management (Professor Role)

#### View Today's Attendance
1. Switch to **Professor** tab
2. Select **Validar Presenças**
3. Click on today's date in calendar
4. Verify:
   - All attendance records appear
   - Grouped by class
   - Entry/exit times shown
   - Validation status visible

#### Validate Attendance
1. Review attendance records
2. Click **Validar** on pending records
3. Verify status changes to "Validado"
4. Optional: **Invalidar** if needed

#### Filter by Class
1. Click on class filter buttons
2. Verify only selected class shows
3. Click "Todas" to see all again

---

### 5️⃣ Advanced Admin Features

#### Manage Student Details
1. Switch to **Admin** tab
2. Select **Gerenciar Alunos**
3. Click on a student from list
4. Verify details panel shows:
   - Student information
   - Today's attendance
   - Entry/exit status
   - All presence records

#### Edit Student Information
1. In **Gerenciar Alunos**
2. Select a student
3. Click **Editar Informações**
4. Change name or class
5. Click **Salvar**
6. Verify changes are saved

#### View Today's Attendance Per Student
1. In **Gerenciar Alunos**
2. Select a student who has attendance today
3. Verify "Presenças de Hoje" panel shows:
   - Current status (Em Aula / Fora da Aula)
   - Entry and exit counts
   - Timeline of all records

#### Manual Exit Registration
1. Select student who is "Em Aula"
2. Click **Registrar Saída Manual**
3. Confirm action
4. Verify:
   - Exit is registered
   - Status changes to "Fora da Aula"
   - Exit count increments

#### Delete Face Embeddings
1. Select a student
2. Scroll to "Ações Administrativas"
3. Click **Deletar Embeddings**
4. Confirm action
5. Note: Student will need to re-register photos
6. Test: Try face recognition - should fail
7. Re-register photos via **Registrar Aluno**

#### Delete Student
1. Select a student (use test student)
2. Click **Deletar Aluno (Permanente)**
3. Confirm action
4. Verify:
   - Student removed from list
   - Cannot be recognized anymore

---

### 6️⃣ List and Search Features

#### Search Students
1. Go to **Turmas e Alunos**
2. Use search box to find student by name
3. Filter by class using buttons
4. Verify filtering works correctly

---

## 🧪 Edge Cases to Test

### Recognition Edge Cases
- [ ] No face in camera (should show error)
- [ ] Multiple faces in camera (depends on backend logic)
- [ ] Poor lighting conditions
- [ ] Different angles/expressions from registration
- [ ] Unknown person (should not recognize)

### Validation Edge Cases
- [ ] Student not validated tries to register attendance
- [ ] Verify "Aguardando validação" message appears
- [ ] Professor validates student
- [ ] Try attendance again - should work now

### Entry/Exit Logic
- [ ] Entry → Entry (should register as exit after first)
- [ ] Exit → Exit (should be prevented or register as entry)
- [ ] Manual exit when already out (should show error)
- [ ] Multiple entries/exits in same day

### Data Integrity
- [ ] Delete student with attendance records
- [ ] Delete class with students assigned
- [ ] Delete professor with assigned classes
- [ ] Update student to different class
- [ ] Delete embeddings and re-register

---

## 📊 Expected Backend Responses

### Successful Recognition
```json
{
  "reconhecido": true,
  "aluno_id": 1,
  "aluno_nome": "João Silva",
  "confianca": 0.95,
  "metodo": "face_recognition",
  "presenca_registrada": true,
  "tipo_registro": "entrada"
}
```

### Failed Recognition
```json
{
  "reconhecido": false,
  "mensagem": "Face not recognized",
  "confianca": 0.45
}
```

### Pending Validation
```json
{
  "reconhecido": true,
  "aluno_nome": "João Silva",
  "mensagem": "Student pending professor validation",
  "presenca_registrada": false
}
```

---

## ✅ Testing Checklist

### Core Features
- [ ] Class creation and deletion
- [ ] Professor registration with class assignment
- [ ] Student registration with multiple photos
- [ ] Face recognition in test mode
- [ ] Face recognition with attendance
- [ ] Automatic entry/exit detection
- [ ] Student validation by professor
- [ ] Attendance validation by professor

### Advanced Features
- [ ] Student information editing
- [ ] Today's attendance view per student
- [ ] Manual exit registration
- [ ] Face embeddings deletion
- [ ] Student deletion
- [ ] Calendar navigation for attendance
- [ ] Class-based filtering
- [ ] Search functionality

### UI/UX
- [ ] Loading states show correctly
- [ ] Error messages are clear
- [ ] Success messages confirm actions
- [ ] Confirmation dialogs prevent accidents
- [ ] Navigation between screens works
- [ ] Data refreshes after changes
- [ ] Responsive design on different screens

---

## 🐛 Known Issues & Limitations

1. **SSL Warning**: LibreSSL warning in backend (doesn't affect functionality)
2. **Camera Access**: Requires HTTPS in production (localhost works with HTTP)
3. **Single Face**: System processes one face at a time
4. **Photo Quality**: Best results with clear, well-lit photos
5. **Professor ID**: Currently hardcoded as 1 for validation (can be improved)

---

## 🎯 Success Criteria

All integrations are successful if:
1. ✅ All CRUD operations work (Create, Read, Update, Delete)
2. ✅ Face recognition correctly identifies registered students
3. ✅ Entry/exit logic works automatically
4. ✅ Professor validation workflow functions
5. ✅ All admin features accessible and functional
6. ✅ No console errors or broken API calls
7. ✅ Data persists correctly in database
8. ✅ UI provides clear feedback for all actions

---

## 📝 Test Results Log

Document your testing results:

| Feature | Status | Notes |
|---------|--------|-------|
| Create Class | ⬜ | |
| Register Professor | ⬜ | |
| Register Student | ⬜ | |
| Test Recognition | ⬜ | |
| Register Attendance | ⬜ | |
| Entry/Exit Logic | ⬜ | |
| Validate Student | ⬜ | |
| Validate Attendance | ⬜ | |
| Edit Student | ⬜ | |
| Delete Embeddings | ⬜ | |
| Manual Exit | ⬜ | |
| Delete Student | ⬜ | |
| Search/Filter | ⬜ | |

---

## 🚨 If Something Fails

1. **Check Backend Logs**: Terminal running backend
2. **Check Frontend Console**: Browser DevTools (F12)
3. **Verify API Response**: Use browser Network tab
4. **Check Database**: Supabase dashboard
5. **Restart Servers**: If needed, stop and restart both
6. **Clear Browser Cache**: Sometimes needed for JS changes

---

## 🎉 Happy Testing!

The system is fully integrated and ready for comprehensive testing. All backend endpoints have visual representations, and all features are accessible through the intuitive UI.
