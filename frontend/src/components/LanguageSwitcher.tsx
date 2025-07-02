import { useTranslation } from 'react-i18next';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
  ];

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
  };

  return (
    <ToggleButtonGroup
      size="small"
      exclusive
      value={i18n.language}
      onChange={(_, val) => val && handleLanguageChange(val)}
    >
      {languages.map(language => (
        <ToggleButton
          key={language.code}
          value={language.code}
          aria-label={language.name}
        >
          <span style={{ marginRight: 4 }}>{language.flag}</span>
          {language.code.toUpperCase()}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
};

export default LanguageSwitcher;
