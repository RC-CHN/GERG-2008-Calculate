<script setup>
import { ref } from 'vue';

// Component data definition
const available_components = ref([
    { name: 'Methane', formula: 'CH₄', chineseName: '甲烷' },
    { name: 'Nitrogen', formula: 'N₂', chineseName: '氮气' },
    { name: 'CarbonDioxide', formula: 'CO₂', chineseName: '二氧化碳' },
    { name: 'Ethane', formula: 'C₂H₆', chineseName: '乙烷' },
    { name: 'Propane', formula: 'C₃H₈', chineseName: '丙烷' },
    { name: 'Water', formula: 'H₂O', chineseName: '水' },
    { name: 'HydrogenSulfide', formula: 'H₂S', chineseName: '硫化氢' },
    { name: 'CarbonMonoxide', formula: 'CO', chineseName: '一氧化碳' },
    { name: 'Oxygen', formula: 'O₂', chineseName: '氧气' },
    { name: 'Isobutane', formula: 'i-C₄H₁₀', chineseName: '异丁烷' },
    { name: 'Butane', formula: 'n-C₄H₁₀', chineseName: '正丁烷' },
    { name: 'Isopentane', formula: 'i-C₅H₁₂', chineseName: '异戊烷' },
    { name: 'Pentane', formula: 'n-C₅H₁₂', chineseName: '正戊烷' },
    { name: 'Hexane', formula: 'n-C₆H₁₄', chineseName: '己烷' },
    { name: 'Heptane', formula: 'n-C₇H₁₆', chineseName: '庚烷' },
    { name: 'Octane', formula: 'n-C₈H₁₈', chineseName: '辛烷' },
    { name: 'Nonane', formula: 'n-C₉H₂₀', chineseName: '壬烷' },
    { name: 'Decane', formula: 'n-C₁₀H₂₂', chineseName: '癸烷' },
    { name: 'Helium', formula: 'He', chineseName: '氦气' },
    { name: 'Argon', formula: 'Ar', chineseName: '氩气' },
]);

const defaultValues = [
  { name: 'Methane', fraction: 0.961651 },
  { name: 'Nitrogen', fraction: 0.008606 },
  { name: 'CarbonDioxide', fraction: 0.004567 },
  { name: 'Ethane', fraction: 0.01998 },
  { name: 'Propane', fraction: 0.003859 },
  { name: 'Butane', fraction: 0.000950 },
  { name: 'Pentane', fraction: 0.000138 },
  { name: 'Hexane', fraction: 0.000249 },
];

// Input data refs
const T = ref(298.15);
const P_kPa = ref(101.325);
const hydrogen_fraction = ref(0.0);
const base_components = ref(JSON.parse(JSON.stringify(defaultValues)));

// State refs
const result = ref(null);
const error = ref(null);
const loading = ref(false);

// Functions
function addComponent() {
  base_components.value.push({ name: '', fraction: 0.0 });
}

function removeComponent(index) {
  base_components.value.splice(index, 1);
}

function loadDefaultValues() {
  base_components.value = JSON.parse(JSON.stringify(defaultValues));
  hydrogen_fraction.value = 0;
}

async function calculate() {
  loading.value = true;
  result.value = null;
  error.value = null;

  const payload = {
    T: T.value,
    P_kPa: P_kPa.value,
    hydrogen_fraction: hydrogen_fraction.value,
    base_components: base_components.value.reduce((acc, comp) => {
      if (comp.name && comp.fraction > 0) {
        acc[comp.name] = comp.fraction;
      }
      return acc;
    }, {}),
  };

  try {
    const response = await fetch('http://127.0.0.1:8000/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    result.value = data;

  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="container">
    <h1>GERG-2008 天然气性质计算器</h1>

    <div class="main-layout">
      <!-- Input Column -->
      <div class="input-column">
        <div class="card">
          <div class="card-header">
            <h2>输入参数</h2>
          </div>
          <div class="input-group">
            <label for="temperature">温度 (K)</label>
            <input id="temperature" type="number" v-model.number="T" />
          </div>
          <div class="input-group">
            <label for="pressure">压力 (kPa)</label>
            <input id="pressure" type="number" v-model.number="P_kPa" />
          </div>
          <div class="input-group">
            <label for="hydrogen">氢气摩尔分数 (0-1)</label>
            <input id="hydrogen" type="number" v-model.number="hydrogen_fraction" step="0.01" />
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h2>基础组分</h2>
            <button @click="loadDefaultValues" class="load-defaults-btn">载入典型组分</button>
          </div>
          <div v-for="(component, index) in base_components" :key="index" class="component-row">
            <select v-model="component.name">
              <option disabled value="">请选择一个组分</option>
              <option v-for="comp in available_components" :key="comp.name" :value="comp.name">
                {{ comp.name }} ({{ comp.formula }}) - {{ comp.chineseName }}
              </option>
            </select>
            <input type="number" v-model.number="component.fraction" placeholder="摩尔分数" step="0.0001" />
            <button @click="removeComponent(index)" class="remove-btn">移除</button>
          </div>
          <button @click="addComponent" class="add-btn">添加组分</button>
        </div>
         <button @click="calculate" class="calculate-btn" :disabled="loading">
            {{ loading ? '计算中...' : '计 算' }}
          </button>
      </div>

      <!-- Results Column -->
      <div class="results-column">
        <div class="card sticky-card">
           <div class="card-header">
            <h2>计算结果</h2>
          </div>
          <div v-if="loading" class="loading-spinner">
            <p>正在计算，请稍候...</p>
          </div>
          <div v-if="error" class="error-card">
            <h3>错误</h3>
            <p>{{ error }}</p>
          </div>
          <div v-if="result" class="result-content">
            <p class="result-main"><strong>压缩因子 (Z):</strong> <span>{{ result.compression_factor?.toFixed(6) }}</span></p>
            <h3>最终组分比例:</h3>
            <ul class="result-list">
              <li v-for="(frac, comp) in result.final_components" :key="comp">
                <span>{{ comp }}</span>
                <span>{{ frac.toFixed(6) }}</span>
              </li>
            </ul>
          </div>
           <div v-if="!result && !error && !loading" class="placeholder-text">
            <p>点击“计算”后，结果将在此处显示。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
    .container {
      max-width: 1600px;
      margin: 0 auto;
      padding: 2rem;
    }
    
    h1 {
      text-align: center;
      color: var(--text-color);
      font-weight: 600;
      margin-bottom: 2.5rem;
      font-size: 2.2rem;
    }
    
    .main-layout {
      display: flex;
      gap: 2rem;
      align-items: flex-start;
    }
    
    .input-column {
      flex: 2;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
    
    .results-column {
      flex: 1;
    }
    
    .card {
      background: var(--card-bg-color);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 4px 12px var(--shadow-color);
    }
    
    .sticky-card {
      position: sticky;
      top: 2rem;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--border-color);
    }
    
    h2 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
    }
    
    .input-group, .component-row {
      display: grid;
      gap: 1rem;
      margin-bottom: 1.25rem;
    }

    .input-group {
      grid-template-columns: 1fr 3fr;
       align-items: center;
    }
    
    .component-row {
      grid-template-columns: 3fr 2fr auto;
      align-items: center;
    }
    
    label {
      font-weight: 500;
      text-align: right;
      padding-right: 1rem;
    }
    
    input, select {
      padding: 0.6rem 1rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      font-size: 1rem;
      width: 100%;
      box-sizing: border-box;
    }
    
    button {
      padding: 0.6rem 1.5rem;
      border: 1px solid transparent;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }
    
    .load-defaults-btn {
      background-color: transparent;
      color: var(--primary-color);
      border-color: var(--primary-color);
    }
    
    .add-btn {
      background-color: var(--primary-color);
      justify-self: start;
    }
    
    .calculate-btn {
      background-color: var(--success-color);
      font-size: 1.2rem;
      padding: 0.8rem;
    }
     .calculate-btn:disabled {
      background-color: #6c757d;
      cursor: not-allowed;
    }
    
    .remove-btn {
      background-color: var(--danger-color);
      padding: 0.6rem 1rem;
    }
    
    .result-content .result-main {
      font-size: 1.5rem;
      font-weight: 600;
      padding: 1rem;
      background-color: #e9f7ef;
      border-radius: 8px;
      text-align: center;
      margin-bottom: 1.5rem;
    }
    
    .result-main span {
        color: var(--success-color);
    }
    
    .result-list {
        list-style: none;
        padding: 0;
        max-height: 400px;
        overflow-y: auto;
    }

    .result-list li {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0.5rem;
        border-bottom: 1px solid #f1f3f5;
    }

    .result-list li:last-child {
        border-bottom: none;
    }

    .error-card {
        background-color: #fff0f0;
        color: #d94a28;
        border: 1px solid #ffc0c0;
        border-radius: 8px;
        padding: 1rem;
    }
    .placeholder-text, .loading-spinner {
        text-align: center;
        color: #6c757d;
        padding: 4rem 1rem;
    }
</style>
