<?php

//namespace api;

use AmoCRM\Client\AmoCRMApiClient;
use AmoCRM\Exceptions\AmoCRMApiException;
use AmoCRM\Exceptions\AmoCRMoAuthApiException;
use League\OAuth2\Client\Token\AccessToken;
use League\OAuth2\Client\Token\AccessTokenInterface;
use AmoCRM\Client\LongLivedAccessToken;


class AmoClient
{
    private AmoCRMApiClient $apiClient;
    private string $tokenFile;
    private array $credentials; 
    
    public function __construct()
    {
        $this->tokenFile = __DIR__ . '/../config/token.json';
        $credentials = require __DIR__ . '/../config/credentials.php';
        
        $this->apiClient = new AmoCRMApiClient(
            $credentials['client_id'],
            $credentials['client_secret'],
            $credentials['redirect_uri']
        );
        
        $this->apiClient->setAccountBaseDomain($credentials['domain']);
    }

    /**
     * Авторизация в AMO CRM
     * @return AmoCRMApiClient
     * @throws AmoCRMApiException
     * @throws AmoCRMoAuthApiException
     */
    public function authorize(): AmoCRMApiClient
    {
        if (file_exists($this->tokenFile)) {
            $accessToken = json_decode(file_get_contents($this->tokenFile), true);
            
            if (
                isset($accessToken['access_token']) &&
                isset($accessToken['refresh_token']) &&
                isset($accessToken['expires'])
            ) {
                $accessToken = new AccessToken([
                    'access_token' => $accessToken['access_token'],
                    'refresh_token' => $accessToken['refresh_token'],
                    'expires' => $accessToken['expires'],
                    'baseDomain' => $this->apiClient->getAccountBaseDomain(),
                ]);
                
                $this->apiClient->setAccessToken($accessToken)
                    ->onAccessTokenRefresh(
                        function (AccessTokenInterface $accessToken) {
                            $this->saveToken([
                                'access_token' => $accessToken->getToken(),
                                'refresh_token' => $accessToken->getRefreshToken(),
                                'expires' => $accessToken->getExpires(),
                            ]);
                        }
                    );
                
                return $this->apiClient;
            }
        }

        // Если токен не существует или неполный, получаем новый
        $credentials = require __DIR__ . '/../config/credentials.php';
        
        try {
            $longLivedAccessToken = new LongLivedAccessToken($credentials['code']);
            //$accessToken = $this->apiClient->getOAuthClient()->getAccessTokenByCode($credentials['code']);
            
            $this->apiClient->setAccessToken($longLivedAccessToken)
            ->setAccountBaseDomain($credentials['domain']);
            
            return $this->apiClient;
        } catch (AmoCRMoAuthApiException $e) {
            throw $e;
        }
    }

    /**
     * Сохранение токена в файл
     * @param array $token
     * @return void
     */
    private function saveToken(array $token): void
    {
        file_put_contents($this->tokenFile, json_encode($token, JSON_PRETTY_PRINT));
    }
} 