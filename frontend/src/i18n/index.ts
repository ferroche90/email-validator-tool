import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translation files
import enCommon from './locales/en/common.json';
import enValidation from './locales/en/validation.json';
import esCommon from './locales/es/common.json';
import esValidation from './locales/es/validation.json';

const resources = {
  en: {
    common: enCommon,
    validation: enValidation,
  },
  es: {
    common: esCommon,
    validation: esValidation,
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: 'en', // default language
  fallbackLng: 'en',
  debug: process.env.NODE_ENV === 'development',

  interpolation: {
    escapeValue: false, // React already escapes values
  },

  defaultNS: 'common',
  ns: ['common', 'validation'],
});

export default i18n;
