from skills.zarc_skill import check_zarc_policy

# Testando Soja (Deve retornar ELEGIVEL)
print(check_zarc_policy(5208707, "SOJA", 3))

# Testando Feijão (Deve retornar INELEGIVEL)
print(check_zarc_policy(5208707, "FEIJAO", 1))

# Testando algo que não existe (Deve dar PENDENTE)
print(check_zarc_policy(5208707, "ALGODAO", 2))