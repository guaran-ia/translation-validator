// Tooltip texts for Guaraní classification. Values can be overridden by Vite env vars
// e.g. VITE_TOOLTIP_GUARANI_PURO_TITLE, VITE_TOOLTIP_GUARANI_PURO_DESC, etc.
const tips = {
  guarani_puro: {
    title: import.meta.env.VITE_TOOLTIP_GUARANI_PURO_TITLE || "Guaraní puro (o académico)",
    desc: import.meta.env.VITE_TOOLTIP_GUARANI_PURO_DESC || "Forma tradicional y académica del guaraní. Se utiliza en contextos formales y educativos.",
    example: import.meta.env.VITE_TOOLTIP_GUARANI_PURO_EXAMPLE || ""
  },
  jopara: {
    title: import.meta.env.VITE_TOOLTIP_JOPARA_TITLE || "Jopara",
    desc: import.meta.env.VITE_TOOLTIP_JOPARA_DESC || "Mezcla o préstamo léxico entre guaraní y español; combina palabras y estructuras de ambas lenguas.",
    example: import.meta.env.VITE_TOOLTIP_JOPARA_EXAMPLE || 'Ejemplo: "venina na" (venina = español, na = guaraní)'
  },
  jehea: {
    title: import.meta.env.VITE_TOOLTIP_JEHEA_TITLE || "Jehe'a (Guaraní paraguayo)",
    desc: import.meta.env.VITE_TOOLTIP_JEHEA_DESC || "Variante más cotidiana del guaraní en Paraguay; puede incluir rasgos de hibridación con el español.",
    example: import.meta.env.VITE_TOOLTIP_JEHEA_EXAMPLE || ""
  }
};

export default tips;
