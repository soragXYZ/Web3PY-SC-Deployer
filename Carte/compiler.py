from solcx import compile_standard, install_solc

with open("./Greeter.sol", "r") as file:
    sol_file = file.read()

# Compile our Solidity

install_solc("0.8.4")
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Greeter.sol": {"content": sol_file}},
        "settings": {
            "optimizer": { "enabled": False},
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.4",
)

print(compile_sol)