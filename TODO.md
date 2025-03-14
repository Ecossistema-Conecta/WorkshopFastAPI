### 🔹 **Roteiro Atualizado de Novas Rotas e Códigos Auxiliares**  

Além das rotas anteriores, agora os heróis terão **poder de ataque e defesa**, e as batalhas considerarão esses atributos.  

---

### **1️⃣ Rota: Criar um Time de Heróis**  
- **Descrição:** Criar um novo time e associar heróis a ele.  
- **Endpoint:** `POST /teams/`  
- **Código auxiliar:**  
  - Criar um modelo `Team` no banco de dados.  
  - Criar um esquema `TeamSchema`.  
  - Criar relação entre `Team` e `SuperHero`.  

---

### **2️⃣ Rota: Listar Times e Seus Membros**  
- **Descrição:** Retorna todos os times cadastrados e seus membros.  
- **Endpoint:** `GET /teams/`  
- **Código auxiliar:**  
  - Criar um esquema de resposta que inclui os heróis do time.  

---

### **3️⃣ Rota: Adicionar Herói a um Time**  
- **Descrição:** Adiciona um herói já existente a um time.  
- **Endpoint:** `POST /teams/{team_id}/add_hero/{hero_id}`  
- **Código auxiliar:**  
  - Criar uma lógica para associar um herói ao time.  
  - Garantir que um herói não seja adicionado duas vezes ao mesmo time.  

---

### **4️⃣ Rota: Atualizar Informações de um Herói**  
- **Descrição:** Atualiza os atributos do herói, incluindo **ataque e defesa**.  
- **Endpoint:** `PUT /heroes/{hero_id}`  
- **Código auxiliar:**  
  - Adicionar os campos `attack_power` e `defense_power` ao modelo `SuperHero`.  
  - Criar um esquema `SuperHeroUpdateSchema` que inclua esses atributos.  

---

### **5️⃣ Rota: Batalha entre Heróis**  
- **Descrição:** Simula uma batalha entre dois heróis com base nos atributos `attack_power` e `defense_power`.  
- **Endpoint:** `POST /battle/hero_vs_hero`  
- **Código auxiliar:**  
  - Criar uma função que compara `attack_power` de um herói contra `defense_power` do outro.  
  - Adicionar um fator aleatório para tornar os combates mais imprevisíveis.  
  - Retornar o vencedor.  

**📝 Fórmula Sugerida para Batalha entre Heróis:**  
```
Dano = attack_power - (defense_power / 2)
Vence quem reduzir a vida do oponente primeiro.
```

---

### **6️⃣ Rota: Batalha entre Times**  
- **Descrição:** Simula uma batalha entre dois times, levando em conta a soma de `attack_power` e `defense_power` de seus membros.  
- **Endpoint:** `POST /battle/team_vs_team`  
- **Código auxiliar:**  
  - Criar uma função que soma os valores dos atributos dos membros do time.  
  - O time que causar mais dano vence.  

---

### **7️⃣ Rota: Atualizar Informações de um Time**  
- **Descrição:** Permite alterar nome do time e remover heróis do time.  
- **Endpoint:** `PUT /teams/{team_id}`  
- **Código auxiliar:**  
  - Criar lógica para atualizar o nome do time.  
  - Criar função para remover um herói do time.  

---

### **8️⃣ Rota: Deletar um Time**  
- **Descrição:** Remove um time do banco de dados.  
- **Endpoint:** `DELETE /teams/{team_id}`  
- **Código auxiliar:**  
  - Criar validação para evitar remoção de times com heróis associados.  

---
