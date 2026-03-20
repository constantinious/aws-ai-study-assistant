import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserAttribute,
  CognitoUserPool,
} from 'amazon-cognito-identity-js'
import { useCallback, useEffect, useState } from 'react'

const userPool = new CognitoUserPool({
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_APP_CLIENT_ID,
})

interface AuthState {
  isAuthenticated: boolean
  email: string | null
  isLoading: boolean
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    email: null,
    isLoading: true,
  })

  useEffect(() => {
    const user = userPool.getCurrentUser()
    if (!user) {
      setState({ isAuthenticated: false, email: null, isLoading: false })
      return
    }
    user.getSession((err: Error | null, session: any) => {
      if (err || !session?.isValid()) {
        setState({ isAuthenticated: false, email: null, isLoading: false })
        return
      }
      const idToken = session.getIdToken().getJwtToken()
      localStorage.setItem('id_token', idToken)
      setState({
        isAuthenticated: true,
        email: session.getIdToken().payload.email,
        isLoading: false,
      })
    })
  }, [])

  const signIn = useCallback((email: string, password: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool })
      const authDetails = new AuthenticationDetails({ Username: email, Password: password })

      user.authenticateUser(authDetails, {
        onSuccess(session) {
          const idToken = session.getIdToken().getJwtToken()
          localStorage.setItem('id_token', idToken)
          setState({ isAuthenticated: true, email, isLoading: false })
          resolve()
        },
        onFailure(err) {
          reject(new Error(err.message ?? 'Sign in failed'))
        },
      })
    })
  }, [])

  const signUp = useCallback((email: string, password: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const attributes = [new CognitoUserAttribute({ Name: 'email', Value: email })]
      userPool.signUp(email, password, attributes, [], (err) => {
        if (err) {
          reject(new Error(err.message ?? 'Sign up failed'))
        } else {
          resolve()
        }
      })
    })
  }, [])

  const confirmSignUp = useCallback((email: string, code: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool })
      user.confirmRegistration(code, true, (err) => {
        if (err) reject(new Error(err.message ?? 'Confirmation failed'))
        else resolve()
      })
    })
  }, [])

  const signOut = useCallback(() => {
    const user = userPool.getCurrentUser()
    user?.signOut()
    localStorage.removeItem('id_token')
    setState({ isAuthenticated: false, email: null, isLoading: false })
  }, [])

  return { ...state, signIn, signUp, confirmSignUp, signOut }
}
