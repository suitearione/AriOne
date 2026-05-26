Padrão de Identidade Visual — Logo AriOne

Elemento            Propriedade	        Valor		                Observação

Fonte Global        font-family	        Montserrat', sans-serif		Fonte moderna e geométrica

"Ari" (Prefixo)     font-size       	24px		                Tamanho principal

                    font-weight         300 (Light)                 Elegante e leve

                    color               #00B7EE                   Ciano vibrante (Identidade AriOne)

                    letter-spacing      -1px                        Aproxima as letras para um look premium

"One" (Sufixo)      font-weight         800 (Extra Bold)            Contraste forte com o "Ari"

                    color               #FFFFFF                   Branco puro

Subtítulo           font-size	        10px                        Discreto abaixo do nome

("Tudo em Um")     font-weight	        600 (Semi-Bold)	

                    color	rgba(255, 255, 255, 0.7)              Branco com 70% de opacidade

                    letter-spacing	2px                             Espaçado para legibilidade

                    text-transform	UPPERCASE                       Sempre em maiúsculas
                    
Estrutura de Código Sugerida (HTML/CSS)
Se você precisar replicar isso em outros locais (como telas de login ou relatórios), a estrutura padrão é:

HTML:

html
<div class="logo-title">Ari<span>One</span></div>
<div class="logo-subtitle">Tudo em Um</div>
CSS (Resumo):

css
.logo-title {
    font-family: 'Montserrat'; font-size: 24px; font-weight: 300; 
    color: #00B7EE; letter-spacing: -1px; line-height: 1.1;
}
.logo-title span { font-weight: 800; color: #fff; }
.logo-subtitle {
    font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.7);
    letter-spacing: 2px; text-transform: uppercase;
}
O conjunto dessas configurações cria o que chamamos de "Quiet Luxury UX": um visual que é ao mesmo tempo limpo, moderno e transmite autoridade.

