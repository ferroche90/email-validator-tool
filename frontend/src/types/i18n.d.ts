declare module '*.json' {
  const value: Record<string, unknown>
  export default value
}

declare module '*.css' {
  const content: { [className: string]: string }
  export default content
}

declare module 'i18next' {
  export interface i18n {
    changeLanguage(lng: string): Promise<void>
    language: string
    /**
     * Allows plugins (e.g. initReactI18next) to be attached to the i18next instance.
     * The concrete plugin type is not important for our simplified typings, so we
     * accept a generic plugin type and return `this` to keep the fluent interface intact.
     */
    use(module: Record<string, unknown>): this
    /**
     * Initializes the i18next instance. We don't need strict typings for the
     * options object here – using a generic options type keeps the stub simple while silencing
     * the compiler.
     */
    init(options: Record<string, unknown>): this
  }
  
  const i18nInstance: i18n
  export default i18nInstance
}

declare module 'react-i18next' {
  import { i18n } from 'i18next'
  import { ComponentType } from 'react'
  
  export interface I18nextProviderProps {
    i18n: i18n
    children: React.ReactNode
  }
  
  export const I18nextProvider: ComponentType<I18nextProviderProps>
  
  export function useTranslation(namespaces?: string[]): {
    t: (key: string, defaultValue?: string) => string
    i18n: i18n
  }

  /**
   * Re-exported plugin that binds the given i18next instance to React.
   * Typing it as a generic plugin type is sufficient for our local usage as we don't rely on
   * its shape – we only need it to satisfy TypeScript when we import it.
   */
  export const initReactI18next: Record<string, unknown>
} 