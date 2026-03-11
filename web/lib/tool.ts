export const RSAEncrypt = async (password: string): Promise<string> => {
  const JSEncrypt = (await import('jsencrypt')).default; // PKCS#1 v1.5
  const jsencrypt = new JSEncrypt();
  if (!process.env.NEXT_PUBLIC_RSA_PUBLIC_KEY) {
    return Promise.reject(
      new Error('RSA_PUBLIC_KEY is not defined in environment variables')
    );
  }
  const replacedKey = process.env.NEXT_PUBLIC_RSA_PUBLIC_KEY.replace(
    /\\n/g,
    '\n'
  );
  jsencrypt.setKey(replacedKey);
  console.log('Public Key:', replacedKey);
  return jsencrypt.encrypt(password) || '';
};
