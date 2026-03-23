---
name: nbr15808-extintores
description: >
  Referência técnica para NBR 15808 (extintores portáteis) e NBR 12693 (instalação em edificações).
  Use quando o usuário mencionar: extintores portáteis, NBR 15808, NBR 12693, agentes extintores (PQS ABC/BC, CO2, espuma, água pressurizada), capacidade extintora, unidades extintoras, classes de fogo (A/B/C), risco leve/moderado/alto, distância de percurso, área de cobertura, PNC, ensaio hidrostático, conformidade de extintores, cálculo de quantidade de extintores por pavimento, verificação de extintores em IFC/BIM, IfcFireSuppressionTerminal, ou scripts Python com IfcOpenShell para extintores.
---

# ABNT NBR 15808 – Extintores de Incêndio Portáteis

## Contexto e versão

A norma brasileira vigente para extintores portáteis é a **ABNT NBR 15808**, que consolida os requisitos de segurança, desempenho e marcação para extintores do tipo recarregável e descartável com peso total até **20 kg**.

> A norma se aplica ao próprio equipamento (cilindro, agente, válvula, difusor). Para distribuição e instalação em edificações, use em conjunto com a **NBR 12693** (Sistemas de proteção por extintores) e as **Instruções Técnicas estaduais dos Corpos de Bombeiros**.

---

## 1. Tipos de agente extintor

| Código | Agente | Modo de ação |
|--------|--------|-------------|
| **AP** | Água Pressurizada | Resfriamento |
| **PQS BC** | Pó Químico Seco (bicarbonato de sódio – branco) | Abafamento |
| **PQS ABC** | Pó Químico Seco (monofosfato de amônio – amarelo) | Interrupção da cadeia + abafamento |
| **CO2** | Dióxido de Carbono | Abafamento + resfriamento |
| **Espuma** | Espuma mecânica AFFF 3-6% | Resfriamento + abafamento |

---

## 2. Classes de fogo e adequação dos agentes

| Classe | Material | AP | ABC | BC | CO2 | Espuma |
|--------|----------|----|-----|----|-----|--------|
| **A** – Sólidos (madeira, papel, tecido) | Requerem resfriamento | ✅ | ✅ | ❌ | ❌ | ✅ |
| **B** – Líquidos inflamáveis (gasolina, álcool, diesel) | Requerem abafamento | ❌ | ✅ | ✅ | ✅ | ✅ |
| **C** – Equipamentos elétricos energizados | Exigem agente não condutor | ❌ | ✅ | ✅ | ✅ | ❌ |

> Classes D (metais combustíveis) e K (óleos de cozinha) não são cobertas pela NBR 15808; utilizar normas internacionais.

---

## 3. Capacidade extintora – notação e ensaios

O rating segue o formato `[n]A:[n]B:C`, determinado por ensaios laboratoriais normatizados (NBR 15809):

- **Número antes de A** → unidades extintoras para classe A; cada unidade equivale a uma pilha de madeira de dimensões padronizadas extinta com sucesso
- **Número antes de B** → capacidade para classe B, equivalente à área (em ft²) do recipiente de líquido inflamável extinto; 10B ≈ extinção de recipiente de 10 ft² (≈ 0,93 m²)
- **C** sem número → agente não condutor de eletricidade; não há ensaio de extinção, apenas validação de resistividade elétrica

### Ensaio de capacidade extintora (NBR 15809)

| Classe | Bancada de ensaio | Parâmetro avaliado |
|--------|------------------|--------------------|
| A | Pilha de madeira (cribs) de dimensões normalizadas + papel kraft | Extinção completa da chama |
| B | Bandeja circular com líquido inflamável (heptano ou gasolina) | Extinção completa da chama |
| C | Resistência dielétrica entre bocal e nozzle | Resistência ≥ mínimo normativo |

### Tabela de capacidade por tipo e carga

| Tipo | Carga nominal | Capacidade típica |
|------|--------------|-------------------|
| PQS ABC | 1 kg | 1A:5B:C |
| PQS ABC | 4 kg | 2A:20B:C |
| PQS ABC | 6 kg | 3A:40B:C |
| PQS ABC | 12 kg | 4A:80B:C |
| CO2 | 2 kg | 5B:C |
| CO2 | 4 kg | 10B:C |
| CO2 | 6 kg | 40B:C |
| AP | 10 L | 2A |
| Espuma AFFF | 9 L | 2A:20B |

> Valores indicativos; a capacidade real é a certificada pelo INMETRO no rótulo do equipamento.

A certificação INMETRO é **obrigatória** para todos os extintores comercializados no Brasil.

---

## 4. Pressão

| Parâmetro | Definição |
|-----------|-----------|
| **PNC** | Pressão Nominal de Carregamento (a 23 °C ± 3 °C) |
| **PR** | Pressão de Ruptura |

Relação PR / PNC:
- Pressurização direta, juntas não soldadas: **PR ≥ 5 × PNC** e ≥ 5 MPa
- Pressurização direta, juntas soldadas: **PR ≥ 8 × PNC** e ≥ 5 MPa
- Pressurização indireta, juntas não soldadas: **PR ≥ 4 × PNC** e ≥ 5 MPa
- Pressurização indireta, juntas soldadas: **PR ≥ 7 × PNC** e ≥ 5 MPa

Faixas de temperatura operacional típicas:
- Água / Espuma: 5 °C a 60 °C
- CO2: 0 °C a 55 °C
- PQS: −20 °C a 60 °C

CO2: fator de enchimento máximo = **680 g/L**

---

## 5. Marcações obrigatórias no cilindro

1. Nome/marca do fabricante
2. Modelo e número de série
3. Data de fabricação
4. Capacidade extintora (ex.: `2A:20B:C`)
5. PNC em MPa
6. Tara (massa do cilindro vazio)
7. Tipo e massa do agente extintor
8. Símbolos pictóricos das classes de fogo cobertas
9. Instruções de operação em pictogramas (PASS: Pull, Aim, Squeeze, Sweep)
10. Identificação e número do certificado INMETRO
11. Cor do cilindro: **vermelho** (RAL 3000)

---

## 6. Vida útil e manutenção

| Tipo | Periodicidade de inspeção | Ensaio hidrostático |
|------|--------------------------|---------------------|
| Água (AP) | Anual | A cada 5 anos |
| PQS ABC/BC | Anual | A cada 5 anos |
| CO2 | Semestral | A cada 5 anos |
| Espuma | Anual | A cada 5 anos |

- **Extintores recarregáveis:** vida útil indefinida, sujeita às inspeções
- **Extintores descartáveis:** vida útil de **5 anos**, carga máxima 1 kg
- Ensaio hidrostático: pressão ≥ 1,5 × PNC por 30 s, em laboratório acreditado
- Norma de manutenção complementar: **NBR 12962**

---

---

## 7. NBR 12693 – Instalação e distribuição de extintores

### 7.1 Classificação do risco da edificação

| Risco | Descrição | Exemplos |
|-------|-----------|---------|
| **Leve** | Baixa carga combustível, baixa probabilidade de ignição | Escritórios, escolas, residências, igrejas |
| **Moderado** | Carga combustível média ou processo com líquidos inflamáveis em pequena escala | Depósitos de mercadorias, comércio varejista, oficinas leves |
| **Alto** | Alta carga combustível ou grande quantidade de líquidos inflamáveis | Indústrias, postos de combustível, depósitos de produtos químicos |

### 7.2 Número mínimo de unidades extintoras – Classe A

Cada **unidade extintora A** cobre uma área máxima de pavimento conforme o risco:

| Risco | Área máxima coberta por 1 unidade A | Distância máx. a percorrer |
|-------|-------------------------------------|---------------------------|
| Leve | 500 m² | 20 m |
| Moderado | 250 m² | 20 m |
| Alto | 150 m² | 15 m |

**Cálculo da quantidade mínima de extintores classe A:**

```
N_extintores_A = ceil(Área_pavimento / Área_cobertura_por_unidade)
Unidades_extintoras_necessárias = ceil(Área_pavimento / Área_por_unidade)
```

Exemplo: escritório de 600 m² (risco leve):
- Unidades necessárias = ceil(600 / 500) = 2 unidades A
- Um extintor `2A:20B:C` contribui com 2 unidades A → 1 extintor suficiente

### 7.3 Número mínimo de unidades extintoras – Classe B

Para líquidos inflamáveis, a proteção é calculada por área de superfície do líquido:

| Risco | Unidades B por m² de superfície de líquido | Distância máx. |
|-------|---------------------------------------------|----------------|
| Moderado | 1 unidade B / m² (mínimo 20B) | 15 m |
| Alto | 2 unidades B / m² (mínimo 40B) | 15 m |

Para equipamentos elétricos (Classe C): qualquer extintor adequado para C (CO2 ou PQS) na mesma localização do equipamento.

### 7.4 Regras de instalação física

| Requisito | Valor |
|-----------|-------|
| Altura do manípulo | Entre **10 cm e 1,60 m** do piso acabado |
| Extintor ≤ 4 kg / 4 L | Altura máxima do manípulo: **1,60 m** |
| Extintor > 4 kg / 4 L | Altura máxima do manípulo: **1,00 m** |
| Posição | Vertical (exceto CO2 sobre rodas) |
| Piso | Não apoiar diretamente no piso (usar suporte ou gancho) |
| Sinalização | Conforme NBR 7195 (placa fotoluminescente) |
| Distância mínima entre extintores | Não definida; conforme distância máxima de percurso |

### 7.5 Mínimo obrigatório por pavimento

- **Pelo menos 1 extintor por pavimento**, independentemente da área
- Para edificações com área ≤ 50 m²: 1 extintor com capacidade mínima `1A:5B:C`

### 7.6 Property set complementar para instalação (NBR 12693)

Adicionar ao modelo IFC em `Pset_FireExtinguisher_NBR12693`:

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `RiskClass` | IfcLabel | "Leve" \| "Moderado" \| "Alto" |
| `CoveredArea_m2` | IfcAreaMeasure | Área de pavimento protegida por este extintor |
| `TravelDistance_m` | IfcLengthMeasure | Distância máxima de percurso até o extintor |
| `MountingHeight_m` | IfcLengthMeasure | Altura do manípulo em relação ao piso |
| `SignageCompliant` | IfcBoolean | Sinalização conforme NBR 7195 |
| `FloorLevel` | IfcLabel | Identificação do pavimento |

### 7.7 Script Python: cálculo de extintores necessários por andar

```python
import math

def calcular_extintores_nbr12693(area_m2: float, risco: str, tem_liquido_inflamavel: bool = False,
                                  area_liquido_m2: float = 0.0):
    """
    Calcula o número mínimo de extintores e unidades extintoras
    conforme NBR 12693.

    Returns: dict com extintores_A, unidades_A, extintores_BC, unidades_B
    """
    risco = risco.lower()
    config = {
        "leve":    {"area_por_unidade_A": 500, "dist_A": 20, "dist_B": 15},
        "moderado": {"area_por_unidade_A": 250, "dist_A": 20, "dist_B": 15, "B_por_m2": 1, "B_min": 20},
        "alto":    {"area_por_unidade_A": 150, "dist_A": 15, "dist_B": 15, "B_por_m2": 2, "B_min": 40},
    }
    if risco not in config:
        raise ValueError(f"Risco inválido: {risco}. Use 'leve', 'moderado' ou 'alto'.")

    c = config[risco]

    # Unidades extintoras classe A
    unidades_A = math.ceil(area_m2 / c["area_por_unidade_A"])
    unidades_A = max(unidades_A, 1)  # mínimo 1 por pavimento

    # Unidades extintoras classe B (líquidos inflamáveis)
    unidades_B = 0
    if tem_liquido_inflamavel and area_liquido_m2 > 0:
        fator = c.get("B_por_m2", 1)
        b_min = c.get("B_min", 20)
        unidades_B = max(math.ceil(area_liquido_m2 * fator), b_min)

    return {
        "unidades_A_necessarias": unidades_A,
        "unidades_B_necessarias": unidades_B,
        "dist_max_percurso_A_m": c["dist_A"],
        "dist_max_percurso_B_m": c["dist_B"],
        "risco": risco,
        "area_m2": area_m2,
    }

# Exemplo: galpão de 800 m² risco moderado com 5 m² de líquido inflamável
resultado = calcular_extintores_nbr12693(800, "moderado", True, 5.0)
print(resultado)
# → unidades_A=4, unidades_B=20
```

### 7.8 Script Python: verificar distribuição de extintores em modelo IFC

```python
import ifcopenshell
import ifcopenshell.util.element as util
import math

def verificar_distribuicao_nbr12693(ifc_path: str):
    """
    Verifica se cada pavimento tem ao menos 1 extintor
    e se a cobertura de área está adequada.
    """
    model = ifcopenshell.open(ifc_path)
    relatorio = []

    for andar in model.by_type("IfcBuildingStorey"):
        # Coletar extintores do pavimento
        extintores = [
            e for e in model.by_type("IfcFireSuppressionTerminal")
            if util.get_container(e) and util.get_container(e).GlobalId == andar.GlobalId
        ]

        # Área do pavimento (via QuantitySet)
        qsets = util.get_psets(andar, qtos_only=True)
        area = 0.0
        for qset in qsets.values():
            area = qset.get("NetFloorArea", qset.get("GrossFloorArea", 0.0)) or area

        # Calcular unidades A disponíveis
        unidades_A_disponiveis = 0
        for e in extintores:
            pset = util.get_psets(e).get("Pset_FireExtinguisher_NBR15808", {})
            capacidade = pset.get("ExtinguishingCapacity", "")
            # Extrair número de A do rating (ex: "2A:20B:C" → 2)
            import re
            match = re.search(r"(\d+)A", capacidade)
            if match:
                unidades_A_disponiveis += int(match.group(1))

        # Calcular necessidade (assumindo risco moderado se não definido)
        necessario = math.ceil(area / 250) if area > 0 else 1

        relatorio.append({
            "pavimento": andar.Name,
            "area_m2": round(area, 1),
            "extintores_presentes": len(extintores),
            "unidades_A_disponiveis": unidades_A_disponiveis,
            "unidades_A_necessarias": necessario,
            "conforme": len(extintores) >= 1 and unidades_A_disponiveis >= necessario,
        })

    return relatorio
```

---

## 8. Representação em IFC

### Entidade principal

```
IfcFireSuppressionTerminal (IFC 4.x)
  PredefinedType: FIREEXTINGUISHER  ← usar UserDefinedType se não disponível
```

A entidade pertence ao domínio `IfcPlumbingFireProtectionDomain`.

### Property set recomendado (customizado)

Não existe um `Pset` padrão buildingSMART específico para extintores portáteis. Usar:

**`Pset_FireExtinguisher_NBR15808`**

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `ExtinguisherType` | IfcLabel | "AP" \| "PQS_ABC" \| "PQS_BC" \| "CO2" \| "AFFF" |
| `ExtinguishingCapacity` | IfcLabel | Ex: "2A:20B:C" |
| `AgentMass_kg` | IfcMassMeasure | Massa do agente em kg |
| `NominalChargingPressure_PNC` | IfcPressureMeasure | PNC em Pa |
| `RupturePressure_PR` | IfcPressureMeasure | PR em Pa |
| `OperatingTempMin` | IfcThermodynamicTemperatureMeasure | Temperatura mínima em K |
| `OperatingTempMax` | IfcThermodynamicTemperatureMeasure | Temperatura máxima em K |
| `ManufactureDate` | IfcDate | Data de fabricação |
| `LastMaintenanceDate` | IfcDate | Última manutenção |
| `NextHydrostaticTestDate` | IfcDate | Próximo ensaio hidrostático |
| `INMETRO_Certified` | IfcBoolean | Certificação INMETRO |
| `INMETRO_CertNumber` | IfcLabel | Número do certificado |
| `CylinderColor` | IfcLabel | "RAL3000" (vermelho padrão) |
| `IsDisposable` | IfcBoolean | True = descartável (vida útil 5 anos) |

---

## 8. Python + IfcOpenShell: padrões de uso

### 8.1 Encontrar todos os extintores em um modelo

```python
import ifcopenshell
import ifcopenshell.util.element as util

model = ifcopenshell.open("edificio.ifc")

# Estratégia 1: por tipo de entidade
extintores = model.by_type("IfcFireSuppressionTerminal")

# Estratégia 2: por ObjectType ou Name (modelos sem PredefinedType correto)
extintores_proxy = [
    e for e in model.by_type("IfcBuildingElementProxy")
    if e.Name and "extintor" in e.Name.lower()
]
```

### 8.2 Ler property sets do extintor

```python
def get_extintor_psets(element):
    psets = ifcopenshell.util.element.get_psets(element)
    return psets

for e in extintores:
    psets = get_extintor_psets(e)
    pset_nbr = psets.get("Pset_FireExtinguisher_NBR15808", {})
    capacidade = pset_nbr.get("ExtinguishingCapacity", "N/D")
    tipo = pset_nbr.get("ExtinguisherType", "N/D")
    print(f"{e.Name}: Tipo={tipo}, Capacidade={capacidade}")
```

### 8.3 Validar conformidade com NBR 15808

```python
import ifcopenshell
import ifcopenshell.util.element as util
from datetime import date

TIPOS_VALIDOS = {"AP", "PQS_ABC", "PQS_BC", "CO2", "AFFF"}

def validar_extintor_nbr15808(element):
    psets = util.get_psets(element)
    pset = psets.get("Pset_FireExtinguisher_NBR15808", {})
    erros = []

    tipo = pset.get("ExtinguisherType")
    if not tipo:
        erros.append("ExtinguisherType não definido")
    elif tipo not in TIPOS_VALIDOS:
        erros.append(f"ExtinguisherType inválido: {tipo}")

    capacidade = pset.get("ExtinguishingCapacity")
    if not capacidade:
        erros.append("ExtinguishingCapacity não definida")

    certificado = pset.get("INMETRO_Certified")
    if certificado is False:
        erros.append("Extintor sem certificação INMETRO")

    # Verificar prazo do ensaio hidrostático
    proximo_ensaio = pset.get("NextHydrostaticTestDate")
    if proximo_ensaio:
        data_ensaio = date.fromisoformat(str(proximo_ensaio))
        if data_ensaio < date.today():
            erros.append(f"Ensaio hidrostático vencido em {data_ensaio}")

    return erros

model = ifcopenshell.open("edificio.ifc")
for extintor in model.by_type("IfcFireSuppressionTerminal"):
    erros = validar_extintor_nbr15808(extintor)
    status = "✅ OK" if not erros else f"❌ {', '.join(erros)}"
    print(f"{extintor.Name}: {status}")
```

### 8.4 Relatório de conformidade em CSV

```python
import csv
import ifcopenshell
import ifcopenshell.util.element as util

def gerar_relatorio_extintores(ifc_path, csv_path):
    model = ifcopenshell.open(ifc_path)
    rows = []

    for e in model.by_type("IfcFireSuppressionTerminal"):
        psets = util.get_psets(e)
        pset = psets.get("Pset_FireExtinguisher_NBR15808", {})
        erros = validar_extintor_nbr15808(e)

        # Localização espacial
        espaco = util.get_container(e)
        local = espaco.Name if espaco else "N/D"

        rows.append({
            "GlobalId": e.GlobalId,
            "Nome": e.Name or "",
            "Local": local,
            "Tipo": pset.get("ExtinguisherType", ""),
            "Capacidade": pset.get("ExtinguishingCapacity", ""),
            "Massa_kg": pset.get("AgentMass_kg", ""),
            "INMETRO": pset.get("INMETRO_CertNumber", ""),
            "Proximo_Ensaio": pset.get("NextHydrostaticTestDate", ""),
            "Conformidade": "OK" if not erros else "; ".join(erros),
        })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Relatório salvo em {csv_path} ({len(rows)} extintores)")
```

---

## 9. Perguntas frequentes e respostas rápidas

**Qual extintor usar em sala de servidor?**
CO2 (40B:C ou superior) – não condutor, não deixa resíduo.

**Qual extintor não pode ser usado em fogo elétrico?**
Água pressurizada e espuma (condutores).

**Qual o peso máximo de um extintor portátil pela NBR 15808?**
20 kg no total (cilindro + agente).

**Com que frequência fazer o ensaio hidrostático?**
A cada 5 anos (NBR 12962).

**Extintor ABC serve para classe C?**
Sim – o pó ABC é isolante e adequado para equipamentos elétricos.

**Qual a cor padrão do cilindro?**
Vermelho RAL 3000 para todos os tipos.

**Qual a diferença entre PQS ABC e BC?**
ABC usa monofosfato de amônio (pó amarelo), combate A+B+C. BC usa bicarbonato de sódio (pó branco), combate apenas B+C.