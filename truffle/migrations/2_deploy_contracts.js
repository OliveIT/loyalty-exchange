var LoyaltyExchangeToken = artifacts.require("./LoyaltyExchangeToken.sol");

module.exports = function(deployer) {
  deployer.deploy(LoyaltyExchangeToken);
};
